using Cinematica.Core.Models;

namespace Cinematica.Tests.Setup.Fakers.Models;

internal static class FilmFake
{
    public static Film Valid(
        Director director = default,
        Country country = default,
        params FilmGenre[] filmGenres)
    {
        return new Faker<Film>()
            .RuleFor(film => film.Id, Guid.NewGuid())
            .RuleFor(film => film.DirectorId, _ => director != null ? director.Id : Guid.NewGuid())
            .RuleFor(film => film.CountryId, _ => country != null ? country.Id : Guid.NewGuid())
            .RuleFor(film => film.Name, faker => faker.Random.Word())
            .RuleFor(film => film.OriginalName, default(string))
            .RuleFor(film => film.ReleaseYear,
                faker => faker.Random.Number(min: 1900, max: DateTime.UtcNow.Year).ToString())
            .RuleFor(film => film.RuntimeInMinutes, faker => faker.Random.UShort(min: 15, max: 120))
            .RuleFor(film => film.Synopsis, faker => faker.Lorem.Sentence())
            .RuleFor(film => film.Director, _ => director)
            .RuleFor(film => film.Country, _ => country)
            .RuleFor(film => film.FilmGenres, _ => filmGenres)
            .Generate();
    }

    public static IEnumerable<Film> GetMany(int count = 10)
    {
        return [.. Enumerable.Range(start: 1, count: count).Select(_ => Valid())];
    }
}
