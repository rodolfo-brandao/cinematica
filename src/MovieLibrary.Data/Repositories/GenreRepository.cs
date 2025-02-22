using MovieLibrary.Core.Contracts.Repositories;
using MovieLibrary.Core.Models;
using MovieLibrary.Data.DbContexts;

namespace MovieLibrary.Data.Repositories;

public class GenreRepository(MovieLibraryDbContext movieLibraryDbContextdbContext)
    : Repository<Genre>(movieLibraryDbContextdbContext), IGenreRepository;