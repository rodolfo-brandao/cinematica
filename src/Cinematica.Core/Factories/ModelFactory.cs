using Cinematica.Core.Contracts.Factories;
using Cinematica.Core.Models;

namespace Cinematica.Core.Factories;

public sealed class ModelFactory : IModelFactory
{
    public Country CreateCountry(string name, string isoAlpha3Code) => new()
    {
        Id = Guid.NewGuid(),
        Name = name,
        IsoAlpha3Code = isoAlpha3Code,
        CreatedOn = DateTime.UtcNow,
        UpdatedOn = null,
        IsDisabled = false
    };

    public Director CreateDirector(string name, DateOnly dateOfBirth) => new()
    {
        Id = Guid.NewGuid(),
        Name = name,
        DateOfBirth = dateOfBirth,
        CreatedOn = DateTime.UtcNow,
        UpdatedOn = null,
        IsDisabled = false
    };

    public Genre CreateGenre(string name) => new()
    {
        Id = Guid.NewGuid(),
        Name = name,
        CreatedOn = DateTime.UtcNow,
        UpdatedOn = null,
        IsDisabled = false
    };

    public Movie CreateMovie(Guid directorId, Guid countryId, string name, string originalNane,
        string releaseYear, ushort runtimeInMinutes, string synopsis) => new()
    {
        Id = Guid.NewGuid(),
        DirectorId = directorId,
        CountryId = countryId,
        Name = name,
        OriginalName = originalNane,
        ReleaseYear = releaseYear,
        RuntimeInMinutes = runtimeInMinutes,
        Synopsis = synopsis,
        CreatedOn = DateTime.UtcNow,
        UpdatedOn = null,
        IsDisabled = false
    };

    public User CreateUser(string username, string email, string password, string passwordSalt, string role) => new()
    {
        Id = Guid.NewGuid(),
        Username = username,
        Email = email,
        Password = password,
        PasswordSalt = passwordSalt,
        Role = role,
        CreatedOn = DateTime.UtcNow,
        UpdatedOn = null,
        IsDisabled = false
    };
}