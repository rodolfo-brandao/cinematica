using Cinematica.Core.Models.Abstract;

namespace Cinematica.Core.Models;

public class Director : TrackableEntity
{
    public virtual Guid CountryId { get; protected internal set; }
    public virtual string Name { get; protected internal set; }
    public virtual DateOnly DateOfBirth { get; protected internal set; }

    #region Navigation Properties

    public virtual Country Country { get; protected internal set; }
    public virtual ICollection<Film> Films { get; protected internal set; }

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

    public virtual void AddFilm(Film film)
    {
        Films.Add(film);
    }

    public virtual void RemoveFilm(Film film)
    {
        Films.Remove(film);
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
