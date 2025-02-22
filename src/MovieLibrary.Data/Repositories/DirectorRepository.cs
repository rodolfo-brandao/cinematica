using MovieLibrary.Core.Contracts.Repositories;
using MovieLibrary.Core.Models;
using MovieLibrary.Data.DbContexts;

namespace MovieLibrary.Data.Repositories;

public class DirectorRepository(MovieLibraryDbContext movieLibraryDbContext)
    : Repository<Director>(movieLibraryDbContext), IDirectorRepository;