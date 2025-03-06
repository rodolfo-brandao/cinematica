using Cinematica.Core.Contracts.Units;
using Cinematica.Data.DbContexts;

namespace Cinematica.Data.Units;

public sealed class UnitOfWork(CinematicaDbContext CinematicaDbContext) : IUnitOfWork
{
    public async Task<int> SaveChangesAsync() => await CinematicaDbContext.SaveChangesAsync();
}
