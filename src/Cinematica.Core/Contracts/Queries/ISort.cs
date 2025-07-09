using Cinematica.Core.Models.Abstract;

namespace Cinematica.Core.Contracts.Queries;

/// <summary>
/// Provides base methods for sorting in queries.
/// </summary>
/// <typeparam name="TEntity">The type of the entity to be used as reference in the repository actions,
/// of which must inherit from <see cref="Entity"/>.</typeparam>
public interface ISort<TEntity> where TEntity : Entity
{
    /// <summary>
    /// Sorts entities based on the given field and direction.
    /// </summary>
    /// <param name="field">The entity field to be sorted by.</param>
    /// <param name="direction">The sorting direction ("asc" or "desc").</param>
    /// <param name="queryable">The entities to be sorted.</param>
    /// <returns>A <see cref="IQueryable{T}"/>.</returns>
    IQueryable<TEntity> Sort(string field, string direction, IQueryable<TEntity> entities);
}
