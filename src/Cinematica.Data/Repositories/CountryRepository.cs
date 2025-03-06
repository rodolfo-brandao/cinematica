using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;
using Cinematica.Data.DbContexts;

namespace Cinematica.Data.Repositories;

public class CountryRepository(CinematicaDbContext CinematicaDbContext)
    : Repository<Country>(CinematicaDbContext), ICountryRepository;