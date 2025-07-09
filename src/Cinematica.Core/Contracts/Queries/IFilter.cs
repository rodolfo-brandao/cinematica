using Cinematica.Core.Models.Abstract;

namespace Cinematica.Core.Contracts.Queries;

/// <summary>
/// Provides base methods for filtering in queries.
/// </summary>
/// <typeparam name="TQuery">The type of the class of which holds the properties to be used as query params.</typeparam>
/// <typeparam name="TEntity">The type of the entity to be filtered, of which must inherit from <see cref="Entity"/>.</typeparam>
public interface IFilter<TQuery, TEntity>
    where TEntity : Entity
    where TQuery : IQuery
{
    /// <summary>
    /// Filters entities based on the given query params.
    /// </summary>
    /// <param name="query">The class of which contains the query params.</param>
    /// <param name="entities">The entities to be filtered.</param>
    /// <returns>A <see cref="IQueryable{T}"/>.</returns>
    IQueryable<TEntity> Filter(TQuery query, IQueryable<TEntity> entities);
}
