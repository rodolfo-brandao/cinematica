using Cinematica.Core.Models;

namespace Cinematica.Tests.Setup.Fakers.Models;

internal static class UserFake
{
    private const byte PasswordHashLength = 32;
    private const byte PasswordSaltHashLength = 16;

    private static readonly string[] RoleNames = ["admin", "user"];

    public static User Valid(string? username = null) => new Faker<User>()
        .RuleFor(user => user.Id, _ => Guid.NewGuid())
        .RuleFor(user => user.Username, faker => username ?? faker.Internet.UserName())
        .RuleFor(user => user.Email, faker => faker.Internet.Email())
        .RuleFor(user => user.Password, faker => faker.Random.Hash(length: PasswordHashLength))
        .RuleFor(user => user.PasswordSalt, faker => faker.Random.Hash(length: PasswordSaltHashLength))
        .RuleFor(user => user.Role, faker => faker.PickRandom(RoleNames))
        .RuleFor(user => user.CreatedOn, _ => DateTime.UtcNow)
        .RuleFor(user => user.UpdatedOn, _ => null)
        .RuleFor(user => user.IsDisabled, _ => false)
        .Generate();
}