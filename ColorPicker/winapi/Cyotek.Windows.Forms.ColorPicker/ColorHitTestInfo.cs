using System.Drawing;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  public class ColorHitTestInfo
  {
    #region Public Properties

    public Color Color { get; set; }

    public int Index { get; set; }

    public ColorSource Source { get; set; }

    #endregion
  }
}
