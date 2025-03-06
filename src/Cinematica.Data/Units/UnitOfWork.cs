using Cinematica.Core.Contracts.Units;
using Cinematica.Data.DbContexts;

namespace Cinematica.Data.Units;

public sealed class UnitOfWork(CinematicaDbContext cinematicaDbContext) : IUnitOfWork
{
    public async Task<int> SaveChangesAsync() => await cinematicaDbContext.SaveChangesAsync();
}
