namespace MovieLibrary.Core.Models;

/// <summary>
/// Junction entity to represent the many-to-many relationship between
/// <see cref="Movie"/> and <see cref="Genre"/> entities.
/// </summary>
public class MovieGenre
{
    public virtual Guid MovieId { get; protected internal set; }
    public virtual Guid GenreId { get; protected internal set; }

    #region Navigation Properties

    public virtual Movie Movie { get; protected internal set; }
    public virtual Genre Genre { get; protected internal set; }

    #endregion
}