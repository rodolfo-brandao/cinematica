namespace Cinematica.Core.Models;

/// <summary>
/// Junction entity to represent the many-to-many relationship between
/// <see cref="Film"/> and <see cref="Genre"/> entities.
/// </summary>
public class FilmGenre
{
    public virtual Guid FilmId { get; protected internal set; }
    public virtual Guid GenreId { get; protected internal set; }

    #region Navigation Properties

    public virtual Film Film { get; protected internal set; }
    public virtual Genre Genre { get; protected internal set; }

    #endregion
}