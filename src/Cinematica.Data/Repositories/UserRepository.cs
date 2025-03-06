using Microsoft.EntityFrameworkCore;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;
using Cinematica.Core.Models.Nulls;
using Cinematica.Data.DbContexts;

namespace Cinematica.Data.Repositories;

public class UserRepository(CinematicaDbContext cinematicaDbContext)
    : Repository<User>(cinematicaDbContext), IUserRepository
{
    public async Task<User> GetByUsernameAsync(string username)
    {
        return await DbSet.FirstOrDefaultAsync(user => user.Username.Equals(username)) ?? new NullUser();
    }
}
