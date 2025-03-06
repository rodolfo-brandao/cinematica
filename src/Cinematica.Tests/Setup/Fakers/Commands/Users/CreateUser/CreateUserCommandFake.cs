using System.Collections;
using Cinematica.Application.Commands.Users.CreateUser;

namespace Cinematica.Tests.Setup.Fakers.Commands.Users.CreateUser;

internal class CreateUserCommandFake : IEnumerable<object[]>
{
    private const byte MaxUsernameLength = 50;
    private const byte MinPasswordLength = 6;

    private static string?[] InvalidStringTypeValues => [" ", string.Empty, null];

    public static CreateUserCommand Valid(bool? isAdmin = null) => new Faker<CreateUserCommand>()
        .RuleFor(command => command.Username, faker => faker.Internet.UserName())
        .RuleFor(command => command.Email, faker => faker.Internet.Email())
        .RuleFor(command => command.Password, faker => faker.Random.Hash())
        .RuleFor(command => command.IsAdmin, faker => isAdmin ?? faker.Random.Bool())
        .Generate();

    #region Invalid Commands

    private static CreateUserCommand WithEmptyUsername => new Faker<CreateUserCommand>()
        .RuleFor(command => command.Username, faker => faker.PickRandom(InvalidStringTypeValues))
        .RuleFor(command => command.Email, faker => faker.Internet.Email())
        .RuleFor(command => command.Password, faker => faker.Random.Hash())
        .RuleFor(command => command.IsAdmin, faker => faker.Random.Bool())
        .Generate();

    private static CreateUserCommand WithEmptyEmail => new Faker<CreateUserCommand>()
        .RuleFor(command => command.Username, faker => faker.Internet.UserName())
        .RuleFor(command => command.Email, faker => faker.PickRandom(InvalidStringTypeValues))
        .RuleFor(command => command.Password, faker => faker.Random.Hash())
        .RuleFor(command => command.IsAdmin, faker => faker.Random.Bool())
        .Generate();

    private static CreateUserCommand WithEmptyPassword => new Faker<CreateUserCommand>()
        .RuleFor(command => command.Username, faker => faker.Internet.UserName())
        .RuleFor(command => command.Email, faker => faker.Internet.Email())
        .RuleFor(command => command.Password, faker => faker.PickRandom(InvalidStringTypeValues))
        .RuleFor(command => command.IsAdmin, faker => faker.Random.Bool())
        .Generate();

    private static CreateUserCommand WithExceededUsernameLength => new Faker<CreateUserCommand>()
        .RuleFor(command => command.Username, faker => faker.Random.String(length: MaxUsernameLength + 1))
        .RuleFor(command => command.Email, faker => faker.Internet.Email())
        .RuleFor(command => command.Password, faker => faker.Random.Hash())
        .RuleFor(command => command.IsAdmin, faker => faker.Random.Bool())
        .Generate();

    private static CreateUserCommand WithExceededEmailLength => new Faker<CreateUserCommand>()
        .RuleFor(command => command.Username, faker => faker.Internet.UserName())
        .RuleFor(command => command.Email, faker => faker.Random.String(length: byte.MaxValue + 1))
        .RuleFor(command => command.Password, faker => faker.Random.Hash())
        .RuleFor(command => command.IsAdmin, faker => faker.Random.Bool())
        .Generate();
    
    private static CreateUserCommand WithInvalidEmailFormat => new Faker<CreateUserCommand>()
        .RuleFor(command => command.Username, faker => faker.Internet.UserName())
        .RuleFor(command => command.Email, faker => faker.Random.String())
        .RuleFor(command => command.Password, faker => faker.Random.Hash())
        .RuleFor(command => command.IsAdmin, faker => faker.Random.Bool())
        .Generate();

    private static CreateUserCommand WithTooShortPasswordLength => new Faker<CreateUserCommand>()
        .RuleFor(command => command.Username, faker => faker.Internet.UserName())
        .RuleFor(command => command.Email, faker => faker.Internet.Email())
        .RuleFor(command => command.Password, faker => faker.Random.String(length: MinPasswordLength - 1))
        .RuleFor(command => command.IsAdmin, faker => faker.Random.Bool())
        .Generate();

    #endregion

    public IEnumerator<object[]> GetEnumerator()
    {
        yield return
        [
            WithEmptyUsername
        ];

        yield return
        [
            WithEmptyEmail
        ];

        yield return
        [
            WithEmptyPassword
        ];

        yield return
        [
            WithExceededUsernameLength
        ];

        yield return
        [
            WithExceededEmailLength
        ];

        yield return
        [
            WithInvalidEmailFormat
        ];

        yield return
        [
            WithTooShortPasswordLength
        ];
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}
