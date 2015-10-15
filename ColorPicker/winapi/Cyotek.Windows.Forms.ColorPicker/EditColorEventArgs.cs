using System;
using System.Drawing;

namespace Cyotek.Windows.Forms
{
  public class EditColorEventArgs : EventArgs
  {
    #region Public Constructors

    public EditColorEventArgs(Color color, int colorIndex)
    {
      this.Color = color;
      this.ColorIndex = colorIndex;
    }

    #endregion

    #region Protected Constructors

    protected EditColorEventArgs()
    { }

    #endregion

    #region Public Properties

    public Color Color { get; protected set; }

    public int ColorIndex { get; protected set; }

    #endregion
  }
}
