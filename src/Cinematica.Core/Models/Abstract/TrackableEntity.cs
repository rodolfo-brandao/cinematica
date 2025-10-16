namespace Cinematica.Core.Models.Abstract;

/// <summary>
/// Abstract class to represents an entity that can be tracked.
/// </summary>
public abstract class TrackableEntity : Entity
{
    public DateTime CreatedAt { get; protected internal init; }
    public DateTime? UpdatedAt { get; protected internal set; }
    public bool IsDisabled { get; protected internal set; }

    public abstract TrackableEntity Disable();
    public abstract TrackableEntity Enable();
    public abstract TrackableEntity UpdatedNow();
}
