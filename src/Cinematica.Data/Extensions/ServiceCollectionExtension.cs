using System.Diagnostics.CodeAnalysis;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Cinematica.Core.Contracts.Factories;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Contracts.Services;
using Cinematica.Core.Contracts.Units;
using Cinematica.Core.Factories;
using Cinematica.Data.DbContexts;
using Cinematica.Data.Repositories;
using Cinematica.Data.Services;
using Cinematica.Data.Units;

namespace Cinematica.Data.Extensions;

[ExcludeFromCodeCoverage]
public static class ServiceCollectionExtension
{
    public static IServiceCollection AddCustomDbContext(this IServiceCollection serviceCollection, IConfiguration configuration, string connectionStringKey)
    {
        var connectionString = configuration.GetConnectionString(name: connectionStringKey);
        return serviceCollection.AddDbContext<CinematicaDbContext>(options =>
        {
            options.UseSqlServer(connectionString);
        });
    }

    public static IServiceCollection AddCustomFactories(this IServiceCollection serviceCollection)
    {
        return serviceCollection.AddScoped<IModelFactory, ModelFactory>();
    }

    public static IServiceCollection AddCustomRepositories(this IServiceCollection serviceCollection)
    {
        return serviceCollection
            .AddScoped(typeof(IRepository<>), typeof(Repository<>))
            .AddScoped<ICountryRepository, CountryRepository>()
            .AddScoped<IDirectorRepository, DirectorRepository>()
            .AddScoped<IFilmRepository, FilmRepository>()
            .AddScoped<IUserRepository, UserRepository>();
    }

    public static IServiceCollection AddCustomServices(this IServiceCollection serviceCollection)
    {
        return serviceCollection.AddScoped<ISecurityService, SecurityService>();
    }

    public static IServiceCollection AddCustomUnitsOfWork(this IServiceCollection serviceCollection)
    {
        return serviceCollection.AddScoped<IUnitOfWork, UnitOfWork>();
    }
}
