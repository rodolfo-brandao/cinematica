namespace Cinematica.Core.Models.Abstract;

/// <summary>
/// Abstract class to represent a base entity.
/// </summary>
public abstract class Entity
{
    public Guid Id { get; protected internal init; }
}
