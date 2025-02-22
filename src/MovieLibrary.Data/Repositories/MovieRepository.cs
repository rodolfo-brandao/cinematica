using MovieLibrary.Core.Contracts.Repositories;
using MovieLibrary.Core.Models;
using MovieLibrary.Data.DbContexts;

namespace MovieLibrary.Data.Repositories;

public class MovieRepository(MovieLibraryDbContext movieLibraryDbContext)
    : Repository<Movie>(movieLibraryDbContext), IMovieRepository;
