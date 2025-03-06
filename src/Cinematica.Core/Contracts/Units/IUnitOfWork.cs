namespace Cinematica.Core.Contracts.Units;

/// <summary>
/// Represents a unit capable of managing database transactions belonging to the respective context.
/// </summary>
public interface IUnitOfWork
{
    /// <summary>
    /// Asynchronously saves all changes made in the respective context to the underlying database.
    /// </summary>
    /// <returns>The number of state entries written to the underlying database.</returns>
    Task<int> SaveChangesAsync();
}
