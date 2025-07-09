using Cinematica.Core.Models;

namespace Cinematica.Tests.Setup.Fakers.Models;

internal static class CountryFake
{
    public static Country Valid() => new Faker<Country>()
        .RuleFor(country => country.Id, _ => Guid.NewGuid())
        .RuleFor(country => country.Name, faker => faker.Random.Word())
        .RuleFor(country => country.IsoAlpha3Code, faker => faker.Random.String(length: 3))
        .Generate();

    public static IEnumerable<Country> GetMany(int count = 10)
    {
        return [.. Enumerable.Range(start: 1, count: count).Select(_ => Valid())];
    }
}
