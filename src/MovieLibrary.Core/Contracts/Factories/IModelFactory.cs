using MovieLibrary.Core.Models;

namespace MovieLibrary.Core.Contracts.Factories;

/// <summary>
/// A factory abstraction for a component that can create model instances.
/// </summary>
public interface IModelFactory
{
    Country CreateCountry(string name, string isoAlpha3Code);
    Director CreateDirector(string name, DateOnly dateOfBirth);
    Genre CreateGenre(string name);
    Movie CreateMovie(Guid directorId, Guid countryId, string name, string originalName,
        string releaseYear, ushort runtimeInMinutes, string synopsis);
    User CreateUser(string username, string email, string password, string passwordSalt, string role);
}
