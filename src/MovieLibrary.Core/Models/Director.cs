using MovieLibrary.Core.Models.Abstract;

namespace MovieLibrary.Core.Models;

public class Director : TrackableEntity
{
    public virtual Guid CountryId { get; protected internal set; }
    public virtual string Name { get; protected internal set; }
    public virtual DateOnly DateOfBirth { get; protected internal set; }

    #region Navigation Properties

    public virtual Country Country { get; protected internal set; }
    public virtual ICollection<Movie> Movies { get; protected internal set; }

    #endregion

    public virtual Director ChangeName(string name)
    {
        Name = name;
        return this;
    }

    public virtual Director ChangeDateOfBirth(DateOnly dateOfBirth)
    {
        DateOfBirth = dateOfBirth;
        return this;
    }

    public virtual Director ChangeCountry(Guid countryId)
    {
        CountryId = countryId;
        return this;
    }

    public virtual void AddMovie(Movie movie)
    {
        Movies.Add(movie);
    }

    public virtual void RemoveMovie(Movie movie)
    {
        Movies.Remove(movie);
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
