using Cinematica.Core.Models.Abstract;

namespace Cinematica.Core.Models;

public class Film : TrackableEntity
{
    public virtual Guid DirectorId { get; protected internal set; }
    public virtual Guid CountryId { get; protected internal set; }
    public virtual string Name { get; protected internal set; }
    public virtual string OriginalName { get; protected internal set; }
    public virtual string ReleaseYear { get; protected internal set; }
    public virtual ushort RuntimeInMinutes { get; protected internal set; }
    public virtual string Synopsis { get; protected internal set; }

    #region Navigation Properties

    public virtual Director Director { get; protected internal set; }
    public virtual Country Country { get; protected internal set; }
    public virtual ICollection<FilmGenre> FilmGenres { get; protected internal set; }

    #endregion

    public virtual Film ChangeDirector(Guid directorId)
    {
        DirectorId = directorId;
        return this;
    }

    public virtual Film ChangeCountry(Guid countryId)
    {
        CountryId = countryId;
        return this;
    }

    public virtual Film ChangeName(string name)
    {
        Name = name;
        return this;
    }

    public virtual Film ChangeOriginalName(string originalName)
    {
        OriginalName = originalName;
        return this;
    }

    public virtual Film ChangeReleaseYear(string releaseYear)
    {
        ReleaseYear = releaseYear;
        return this;
    }

    public virtual Film ChangeRuntime(ushort runtimeInMinutes)
    {
        RuntimeInMinutes = runtimeInMinutes;
        return this;
    }

    public virtual Film ChangeSynopsis(string synopsis)
    {
        Synopsis = synopsis;
        return this;
    }

    public virtual Film AddGenre(FilmGenre filmGenre)
    {
        FilmGenres.Add(filmGenre);
        return this;
    }

    public virtual Film RemoveGenre(FilmGenre filmGenre)
    {
        FilmGenres.Remove(filmGenre);
        return this;
    }

    public override TrackableEntity Disable()
    {
        IsDisabled = true;
        return this;
    }

    public override TrackableEntity Enable()
    {
        IsDisabled = false;
        return this;
    }

    public override TrackableEntity UpdatedNow()
    {
        UpdatedAt = DateTime.UtcNow;
        return this;
    }
}