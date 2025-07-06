using Cinematica.Core.Models;

namespace Cinematica.Tests.Setup.Fakers.Models;

internal static class DirectorFake
{
    public static Director Valid() => new Faker<Director>()
        .RuleFor(director => director.Id, _ => Guid.NewGuid())
        .RuleFor(director => director.CountryId, _ => Guid.NewGuid())
        .RuleFor(director => director.Name, faker => faker.Person.FirstName)
        .RuleFor(director => director.DateOfBirth, _ => DateOnly.MinValue)
        .Generate();
}
