using System.Diagnostics.CodeAnalysis;
using System.Reflection;
using Microsoft.EntityFrameworkCore;
using Cinematica.Core.Models;

namespace Cinematica.Data.DbContexts;

[ExcludeFromCodeCoverage]
public sealed class CinematicaDbContext : DbContext
{
    public DbSet<Country> Countries { get; set; }
    public DbSet<Director> Directors { get; set; }
    public DbSet<Movie> Movies { get; set; }
    public DbSet<User> Users { get; set; }

    public CinematicaDbContext(DbContextOptions<CinematicaDbContext> options) : base(options)
    {
        ChangeTracker.LazyLoadingEnabled = default;
        AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", isEnabled: true);
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(Assembly.GetExecutingAssembly());
        base.OnModelCreating(modelBuilder);
    }
}
