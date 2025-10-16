using Cinematica.Core.Models.Abstract;

namespace Cinematica.Core.Models;

public class Country : TrackableEntity
{
    public virtual string Name { get; protected internal set; }

    /// <summary>
    /// A three-letter code defined in ISO 3166-1 to represent countries,
    /// dependent territories and special areas of geographical interest.
    /// </summary>
    public string IsoAlpha3Code { get; protected internal set; }

    #region Navigation Properties

    public virtual ICollection<Director> Directors { get; protected internal set; }
    public virtual ICollection<Film> Films { get; protected internal set; }

    #endregion

    public virtual Country ChangeName(string name)
    {
        Name = name;
        return this;
    }

    public virtual Country ChangeIsoAlpha3Code(string isoAlpha3Code)
    {
        IsoAlpha3Code = isoAlpha3Code;
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
