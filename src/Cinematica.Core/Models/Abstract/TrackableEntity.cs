namespace Cinematica.Core.Models.Abstract;

/// <summary>
/// Abstract class to represents an entity that can be tracked.
/// </summary>
public abstract class TrackableEntity : Entity
{
    public DateTime CreatedOn { get; protected internal init; }
    public DateTime? UpdatedOn { get; protected internal set; }
    public bool IsDisabled { get; protected internal set; }

    public abstract TrackableEntity Disable();
    public abstract TrackableEntity Enable();
    public abstract TrackableEntity UpdatedNow();
}
