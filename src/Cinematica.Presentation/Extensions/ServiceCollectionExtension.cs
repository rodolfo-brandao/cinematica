using System.Diagnostics.CodeAnalysis;
using System.Reflection;
using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Mvc.Authorization;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Cinematica.Application.Utils.Constants;

namespace Cinematica.Presentation.Extensions;

[ExcludeFromCodeCoverage]
internal static class ServiceCollectionExtension
{
    public static IApiVersioningBuilder AddCustomApiVersioning(this IServiceCollection serviceCollection)
    {
        return serviceCollection.AddApiVersioning(options =>
        {
            options.DefaultApiVersion = new ApiVersion(majorVersion: 1, minorVersion: ushort.MinValue);
            options.ReportApiVersions = true;
            options.AssumeDefaultVersionWhenUnspecified = true;
        }).AddApiExplorer(options =>
        {
            options.GroupNameFormat = "'v'VVV";
            options.SubstituteApiVersionInUrl = true;
        });
    }

    public static IServiceCollection AddCustomAuthorizationPolicy(this IServiceCollection serviceCollection, IConfiguration configuration)
    {
        var jwtSecret = configuration.GetSection(key: "Jwt:Secret").Value;
        var jwtSecretBytes = Encoding.ASCII.GetBytes(jwtSecret ?? string.Empty);

        _ = serviceCollection.AddAuthorization(options =>
        {
            options.AddPolicy(
                name: AuthorizationRoles.Admin,
                configurePolicy: policy => policy.RequireClaim("User", allowedValues: AuthorizationRoles.Admin)
            );

            options.AddPolicy(
                name: AuthorizationRoles.User,
                configurePolicy: policy => policy.RequireClaim("User", allowedValues: AuthorizationRoles.User)
            );

        }).AddAuthentication(configureOptions: options =>
        {
            options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
            options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
        }).AddJwtBearer(options =>
        {
            options.RequireHttpsMetadata = default;
            options.SaveToken = default;
            options.TokenValidationParameters = new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(jwtSecretBytes),
                ValidateIssuer = default,
                ValidateAudience = default
            };
        });

        return serviceCollection;
    }

    public static IServiceCollection AddCustomCors(this IServiceCollection services, string policyName)
    {
        return services.AddCors(options => options.AddPolicy(name: policyName, policy =>
        {
            policy.AllowAnyHeader();
            policy.AllowAnyMethod();
            policy.AllowAnyOrigin();
        }));
    }

    public static IMvcBuilder AddCustomMvc(this IServiceCollection serviceCollection)
    {
        return serviceCollection.AddMvc(options =>
        {
            var policy = new AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build();
            options.Filters.Add(new AuthorizeFilter(policy));
        });
    }

    public static IServiceCollection AddCustomRouting(this IServiceCollection serviceCollection)
    {
        return serviceCollection.AddRouting(routeOptions =>
        {
            routeOptions.LowercaseUrls = true;
        });
    }

    public static IServiceCollection AddCustomSwagger(this IServiceCollection serviceCollection, IConfiguration configuration)
    {
        const string bearerTokenFormat = "JWT";
        var openApiInfo = GetOpenApiInfo(configuration);
        return serviceCollection.AddSwaggerGen(options =>
        {

            options.SwaggerDoc(name: "v1", openApiInfo);
            options.AddSecurityDefinition(name: JwtBearerDefaults.AuthenticationScheme, new OpenApiSecurityScheme
            {
                Description =
                    $"{bearerTokenFormat} authorization header using {JwtBearerDefaults.AuthenticationScheme} scheme." +
                    $"\r\n\r\nTo authenticate, simply enter '{JwtBearerDefaults.AuthenticationScheme} <your_access_token>'",
                Name = "Authorization",
                In = ParameterLocation.Header,
                Scheme = JwtBearerDefaults.AuthenticationScheme,
                BearerFormat = bearerTokenFormat,
                Type = SecuritySchemeType.ApiKey
            });

            options.AddSecurityRequirement(new OpenApiSecurityRequirement
            {
                {
                    new OpenApiSecurityScheme
                    {
                        Reference = new OpenApiReference
                        {
                            Id = JwtBearerDefaults.AuthenticationScheme,
                            Type = ReferenceType.SecurityScheme
                        }
                    },
                    Array.Empty<string>()
                }
            });

            var xmlFileName = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
            var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFileName);
            options.IncludeXmlComments(xmlPath);
        });
    }

    #region Private Methods

    private static OpenApiInfo GetOpenApiInfo(IConfiguration configuration)
    {
        return new OpenApiInfo
        {
            Version = "v1",
            Title = configuration.GetSection(key: "OpenApiInfo:Title").Value,
            Description = configuration.GetSection(key: "OpenApiInfo:Description").Value,
            Contact = new OpenApiContact
            {
                Name = configuration.GetSection(key: "OpenApiInfo:Contact:Name").Value,
                Url = new Uri(configuration.GetSection(key: "OpenApiInfo:Contact:Url").Value ?? string.Empty)
            },
            License = new OpenApiLicense
            {
                Name = configuration.GetSection(key: "OpenApiInfo:License:Name").Value,
                Url = new Uri(configuration.GetSection(key: "OpenApiInfo:License:Url").Value ?? string.Empty)
            }
        };
    }

    #endregion
}
