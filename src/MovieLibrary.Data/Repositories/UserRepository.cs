using Microsoft.EntityFrameworkCore;
using MovieLibrary.Core.Contracts.Repositories;
using MovieLibrary.Core.Models;
using MovieLibrary.Core.Models.Nulls;
using MovieLibrary.Data.DbContexts;

namespace MovieLibrary.Data.Repositories;

public class UserRepository(MovieLibraryDbContext movieLibraryDbContext)
    : Repository<User>(movieLibraryDbContext), IUserRepository
{
    public async Task<User> GetByUsernameAsync(string username)
    {
        return await DbSet.FirstOrDefaultAsync(user => user.Username.Equals(username)) ?? new NullUser();
    }
}
