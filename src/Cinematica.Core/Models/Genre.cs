using System.Collections;
using Cinematica.Core.Models.Abstract;

namespace Cinematica.Core.Models;

public class Genre : TrackableEntity
{
    public virtual string Name { get; protected internal set; }

    #region Navigation Properties

    public virtual ICollection<FilmGenre> FilmGenres { get; protected internal set; }

    #endregion

    public virtual Genre ChangeName(string name)
    {
        Name = name;
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