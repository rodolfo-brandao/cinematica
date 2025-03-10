using System.Linq.Expressions;
using Microsoft.EntityFrameworkCore;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models.Abstract;
using Cinematica.Data.DbContexts;

namespace Cinematica.Data.Repositories;

public class Repository<TEntity>(CinematicaDbContext cinematicaDbContext) : IRepository<TEntity>
    where TEntity : Entity
{
    protected readonly DbSet<TEntity> DbSet = cinematicaDbContext.Set<TEntity>();

    public async Task<bool> ExistsAsync(Expression<Func<TEntity, bool>> expression)
    {
        return await Query(expression, isReadOnly: true).AnyAsync();
    }

    public async Task<TEntity> GetByKeyAsync(params object[] keys)
    {
        return await DbSet.FindAsync(keys);
    }

    public async Task<TEntity> InsertAsync(TEntity entity)
    {
        return (await DbSet.AddAsync(entity)).Entity;
    }

    public async Task InsertRangeAsync(params TEntity[] entities)
    {
        await DbSet.AddRangeAsync(entities);
    }

    public IQueryable<TEntity> Query(Expression<Func<TEntity, bool>> expression, string includes = "", bool isReadOnly = false)
    {
        var query = isReadOnly ? DbSet.AsNoTracking() : DbSet;

        foreach (var included in includes.Split(',', StringSplitOptions.RemoveEmptyEntries))
        {
            query = query.Include(navigationPropertyPath: included);
        }

        return query.Where(expression ?? (_ => true));
    }

    public TEntity Remove(TEntity entity)
    {
        return DbSet.Remove(entity).Entity;
    }

    public void RemoveRange(params TEntity[] entities)
    {
        DbSet.RemoveRange(entities);
    }

    public TEntity Update(TEntity entity)
    {
        return DbSet.Update(entity).Entity;
    }

    public void UpdateRange(params TEntity[] entities)
    {
        DbSet.UpdateRange(entities);
    }
}
