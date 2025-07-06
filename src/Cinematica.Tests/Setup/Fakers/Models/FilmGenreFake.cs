using Cinematica.Core.Models;

namespace Cinematica.Tests.Setup.Fakers.Models;

internal static class FilmGenreFake
{
    public static FilmGenre Valid(Film film = default, Genre genre = default) => new Faker<FilmGenre>()
        .RuleFor(filmGenre => filmGenre.Film, _ => film)
        .RuleFor(filmGenre => filmGenre.Genre, _ => genre)
        .Generate();
}
