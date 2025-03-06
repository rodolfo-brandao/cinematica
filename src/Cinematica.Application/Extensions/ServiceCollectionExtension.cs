using System.Diagnostics.CodeAnalysis;
using Microsoft.Extensions.DependencyInjection;
using Cinematica.Application.Commands.Users.CreateUser;

namespace Cinematica.Application.Extensions;

[ExcludeFromCodeCoverage]
public static class ServiceCollectionExtension
{
    public static IServiceCollection AddCustomMediatR(this IServiceCollection serviceCollection)
    {
        return serviceCollection.AddMediatR(configuration =>
        {
            configuration.RegisterServicesFromAssembly(typeof(CreateUserHandler).Assembly);
        });
    }
}
