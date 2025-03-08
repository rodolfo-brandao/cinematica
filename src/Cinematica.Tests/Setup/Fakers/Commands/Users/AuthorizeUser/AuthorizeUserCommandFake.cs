using Cinematica.Application.Commands.Users.AuthorizeUser;

namespace Cinematica.Tests.Setup.Fakers.Commands.Users.AuthorizeUser;

internal class AuthorizeUserCommandFake
{
    public static AuthorizeUserCommand Valid() => new Faker<AuthorizeUserCommand>()
        .RuleFor(command => command.Username, faker => faker.Internet.UserName())
        .RuleFor(command => command.Password, faker => faker.Internet.Password())
        .Generate();
}