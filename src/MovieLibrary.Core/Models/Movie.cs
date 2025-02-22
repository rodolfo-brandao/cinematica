using MovieLibrary.Core.Models.Abstract;

namespace MovieLibrary.Core.Models;

public class Movie : TrackableEntity
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
    public virtual ICollection<MovieGenre> MovieGenres { get; protected internal set; }

    #endregion

    public virtual Movie ChangeDirector(Guid directorId)
    {
        DirectorId = directorId;
        return this;
    }

    public virtual Movie ChangeCountry(Guid countryId)
    {
        CountryId = countryId;
        return this;
    }

    public virtual Movie ChangeName(string name)
    {
        Name = name;
        return this;
    }

    public virtual Movie ChangeOriginalName(string originalName)
    {
        OriginalName = originalName;
        return this;
    }

    public virtual Movie ChangeReleaseYear(string releaseYear)
    {
        ReleaseYear = releaseYear;
        return this;
    }

    public virtual Movie ChangeRuntime(ushort runtimeInMinutes)
    {
        RuntimeInMinutes = runtimeInMinutes;
        return this;
    }

    public virtual Movie ChangeSynopsis(string synopsis)
    {
        Synopsis = synopsis;
        return this;
    }

    public virtual Movie AddGenre(MovieGenre movieGenre)
    {
        MovieGenres.Add(movieGenre);
        return this;
    }

    public virtual Movie RemoveGenre(MovieGenre movieGenre)
    {
        MovieGenres.Remove(movieGenre);
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
        UpdatedOn = DateTime.UtcNow;
        return this;
    }
}