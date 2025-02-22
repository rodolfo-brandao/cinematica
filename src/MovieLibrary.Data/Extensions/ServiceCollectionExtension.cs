using System.Diagnostics.CodeAnalysis;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using MovieLibrary.Core.Contracts.Factories;
using MovieLibrary.Core.Contracts.Repositories;
using MovieLibrary.Core.Contracts.Services;
using MovieLibrary.Core.Contracts.Units;
using MovieLibrary.Core.Factories;
using MovieLibrary.Data.DbContexts;
using MovieLibrary.Data.Repositories;
using MovieLibrary.Data.Services;
using MovieLibrary.Data.Units;

namespace MovieLibrary.Data.Extensions;

[ExcludeFromCodeCoverage]
public static class ServiceCollectionExtension
{
    public static IServiceCollection AddCustomDbContext(this IServiceCollection serviceCollection, IConfiguration configuration, string connectionStringKey)
    {
        var connectionString = configuration.GetConnectionString(name: connectionStringKey);
        return serviceCollection.AddDbContext<MovieLibraryDbContext>(options =>
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
            .AddScoped<IMovieRepository, MovieRepository>()
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
