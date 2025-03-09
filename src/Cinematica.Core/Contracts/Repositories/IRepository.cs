using System.Linq.Expressions;
using Cinematica.Core.Models.Abstract;

namespace Cinematica.Core.Contracts.Repositories;

/// <summary>
/// Base abstraction of a repository, which is capable of performing basic CRUD actions.
/// </summary>
/// <typeparam name="TEntity">The type of the entity to be used as reference in the repository actions,
/// of which must inherit from <see cref="Entity"/>.</typeparam>
public interface IRepository<TEntity> where TEntity : Entity
{
    /// <summary>
    /// Checks whether a given entity exists based according to the given expression.
    /// </summary>
    /// <param name="expression">The expression to search for the entity.</param>
    /// <returns>True if there are any entity that meets the conditions of the given expression, otherwise false.</returns>
    Task<bool> ExistsAsync(Expression<Func<TEntity, bool>> expression);

    /// <summary>
    /// Gets a single entity by its key(s).
    /// </summary>
    /// <param name="keys">The value(s) of the entity key(s).</param>
    /// <returns>The entity if it exists, otherwise null.</returns>
    Task<TEntity> GetByKeyAsync(params object[] keys);

    /// <summary>
    /// Inserts the given entity into the database.
    /// </summary>
    /// <param name="entity">The entity to be inserted.</param>
    /// <returns>The newly added entity.</returns>
    Task<TEntity> InsertAsync(TEntity entity);

    /// <summary>
    /// Inserts a set of entities into the database.
    /// </summary>
    /// <param name="entities">The entities to be inserted.</param>
    Task InsertRangeAsync(params TEntity[] entities);

    /// <summary>
    /// Performs a query in the database based on the conditions passed in the expression.
    /// </summary>
    /// <param name="expression">The expression containing the conditions to be used as query in the database.</param>
    /// <param name="includes">The name of the navigation properties to be loaded in the query, separated my comma.</param>
    /// <param name="isReadOnly">Indicates whether the entities found in the query should be read-only or not,
    /// defining whether they can be modified.</param>
    /// <returns>A <see cref="IQueryable{T}"/> of TEntity.</returns>
    IQueryable<TEntity> Query(Expression<Func<TEntity, bool>> expression, string includes = "", bool isReadOnly = default);

    /// <summary>
    /// Removes the given entity from the database.
    /// </summary>
    /// <param name="entity">The entity to be removed.</param>
    /// <returns>The newly removed entity.</returns>
    TEntity Remove(TEntity entity);

    /// <summary>
    /// Removes a set of entities from the database.
    /// </summary>
    /// <param name="entities">The entities to be removed.</param>
    void RemoveRange(params TEntity[] entities);

    /// <summary>
    /// Updates the given entity in the database.
    /// </summary>
    /// <param name="entity">The entity to be updated.</param>
    /// <returns>The newly updated entity.</returns>
    TEntity Update(TEntity entity);

    /// <summary>
    /// Updates a set of entities in the database.
    /// </summary>
    /// <param name="entities">The entities to be updated.</param>
    void UpdateRange(params TEntity[] entities);
}
