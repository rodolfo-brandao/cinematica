using Cinematica.Application.Extensions;
using Cinematica.Data.Extensions;
using Cinematica.Presentation.Extensions;
using Cinematica.Presentation.Middlewares;

var builder = WebApplication.CreateBuilder(args);
var configuration = builder.Configuration;

{
    builder.Services.AddControllers();
    builder.Services.AddEndpointsApiExplorer();
    builder.Services.AddCustomApiVersioning();
    builder.Services.AddCustomCors(policyName: "_CinematicaOrigins");
    builder.Services.AddCustomMediatR();
    builder.Services.AddCustomServices();
    builder.Services.AddCustomAuthorizationPolicy(configuration);
    builder.Services.AddCustomDbContext(configuration, connectionStringKey: "DefaultConnection");
    builder.Services.AddCustomRouting();
    builder.Services.AddCustomSwagger(configuration);
    builder.Services.AddCustomFactories();
    builder.Services.AddCustomRepositories();
    builder.Services.AddCustomUnitsOfWork();
    builder.Services.AddCustomMvc();
}

var app = builder.Build();

{
    if (app.Environment.IsDevelopment())
    {
        app.UseDeveloperExceptionPage().AddCustomSwaggerUse();
    }

    app.UseHttpsRedirection();
    app.UseRouting();
    app.UseAuthentication();
    app.UseAuthorization();
    app.UseMiddleware<ExceptionMiddleware>();
    app.MapControllers();
    app.Run();
}
