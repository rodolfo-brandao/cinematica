using Cinematica.Core.Models;

namespace Cinematica.Tests.Setup.Fakers.Models;

internal static class GenreFake
{
    public static Genre Valid() => new Faker<Genre>()
        .RuleFor(genre => genre.Id, _ => Guid.NewGuid())
        .RuleFor(genre => genre.Name, faker => faker.Random.Word())
        .Generate();
}
