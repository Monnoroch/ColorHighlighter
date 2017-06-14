using System;
using System.Drawing;
using System.IO;
#if USEEXTERNALCYOTEKLIBS
using Cyotek.Drawing;

#endif

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  // http://cyotek.com/blog/loading-the-color-palette-from-a-bbm-lbm-image-file-using-csharp

  // http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/#50577411_pgfId-1055819
  // http://www.nomodes.com/aco.html

  /// <summary>
  /// Deserializes color palettes into and from the images and palettes using the  ILBM (IFF Interleaved Bitmap) format.
  /// </summary>
  public class AdobePhotoshopColorSwatchSerializer : PaletteSerializer
  {
    #region Overridden Properties

    /// <summary>
    /// Gets the default extension for files generated with this palette format.
    /// </summary>
    /// <value>The default extension for files generated with this palette format.</value>
    public override string DefaultExtension
    {
      get { return "aco"; }
    }

    /// <summary>
    /// Gets a descriptive name of the palette format
    /// </summary>
    /// <value>The descriptive name of the palette format.</value>
    public override string Name
    {
      get { return "Adobe Photoshop Color Swatch"; }
    }

    #endregion

    #region Overridden Methods

    /// <summary>
    /// Determines whether this instance can read palette from data the specified stream.
    /// </summary>
    /// <param name="stream">The stream.</param>
    /// <returns><c>true</c> if this instance can read palette data from the specified stream; otherwise, <c>false</c>.</returns>
    public override bool CanReadFrom(Stream stream)
    {
      bool result;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      try
      {
        int version;

        // read the version, which occupies two bytes
        // first byte is 0, the second 1 so I assume this is added to make 1
        //version = this.ReadShort(stream);
        version = stream.ReadByte() + stream.ReadByte();

        result = (version == 1 || version == 2);
      }
      catch
      {
        result = false;
      }

      return result;
    }

    /// <summary>
    /// Deserializes the <see cref="ColorCollection" /> contained by the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> that contains the palette to deserialize.</param>
    /// <returns>The <see cref="ColorCollection" /> being deserialized.</returns>
    public override ColorCollection Deserialize(Stream stream)
    {
      AdobePhotoshopColorSwatchFileVersion version;
      ColorCollection results;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      // read the version, which occupies two bytes
      version = (AdobePhotoshopColorSwatchFileVersion)this.ReadInt16(stream);

      if (version != AdobePhotoshopColorSwatchFileVersion.Version1 && version != AdobePhotoshopColorSwatchFileVersion.Version2)
      {
        throw new InvalidDataException("Invalid version information.");
      }

      // the specification states that a version2 palette follows a version1
      // the only difference between version1 and version2 is the inclusion 
      // of a name property. Perhaps there's addtional color spaces as well
      // but we can't support them all anyway
      // I noticed some files no longer include a version 1 palette

      results = this.ReadPalette(stream, version);
      if (version == AdobePhotoshopColorSwatchFileVersion.Version1)
      {
        version = (AdobePhotoshopColorSwatchFileVersion)this.ReadInt16(stream);
        if (version == AdobePhotoshopColorSwatchFileVersion.Version2)
        {
          results = this.ReadPalette(stream, version);
        }
      }

      return results;
    }

    /// <summary>
    /// Serializes the specified <see cref="ColorCollection" /> and writes the palette to a file using the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> used to write the palette.</param>
    /// <param name="palette">The <see cref="ColorCollection" /> to serialize.</param>
    public override void Serialize(Stream stream, ColorCollection palette)
    {
      this.Serialize(stream, palette, AdobePhotoshopColorSwatchColorSpace.Rgb);
    }

    #endregion

    #region Public Members

    public void Serialize(Stream stream, ColorCollection palette, AdobePhotoshopColorSwatchColorSpace colorSpace)
    {
      this.Serialize(stream, palette, AdobePhotoshopColorSwatchFileVersion.Version2, colorSpace);
    }

    public void Serialize(Stream stream, ColorCollection palette, AdobePhotoshopColorSwatchFileVersion version)
    {
      this.Serialize(stream, palette, version, AdobePhotoshopColorSwatchColorSpace.Rgb);
    }

    public void Serialize(Stream stream, ColorCollection palette, AdobePhotoshopColorSwatchFileVersion version, AdobePhotoshopColorSwatchColorSpace colorSpace)
    {
      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      if (palette == null)
      {
        throw new ArgumentNullException("palette");
      }

      if (version == AdobePhotoshopColorSwatchFileVersion.Version2)
      {
        this.WritePalette(stream, palette, AdobePhotoshopColorSwatchFileVersion.Version1, colorSpace);
      }
      this.WritePalette(stream, palette, version, colorSpace);
    }

    #endregion

    #region Protected Members

    protected virtual ColorCollection ReadPalette(Stream stream, AdobePhotoshopColorSwatchFileVersion version)
    {
      int colorCount;
      ColorCollection results;

      results = new ColorCollection();

      // read the number of colors, which also occupies two bytes
      colorCount = this.ReadInt16(stream);

      for (int i = 0; i < colorCount; i++)
      {
        AdobePhotoshopColorSwatchColorSpace colorSpace;
        int value1;
        int value2;
        int value3;
        string name;

        // again, two bytes for the color space
        colorSpace = (AdobePhotoshopColorSwatchColorSpace)(this.ReadInt16(stream));

        value1 = this.ReadInt16(stream);
        value2 = this.ReadInt16(stream);
        value3 = this.ReadInt16(stream);
        this.ReadInt16(stream); // only CMYK supports this field. As we can't handle CMYK colors, we read the value to advance the stream but don't do anything with it

        if (version == AdobePhotoshopColorSwatchFileVersion.Version2)
        {
          int length;

          // need to read the name even though currently our colour collection doesn't support names
          length = ReadInt32(stream);
          name = this.ReadString(stream, length);
        }
        else
        {
          name = string.Empty;
        }

        switch (colorSpace)
        {
          case AdobePhotoshopColorSwatchColorSpace.Rgb:
            int red;
            int green;
            int blue;

            // RGB.
            // The first three values in the color data are red , green , and blue . They are full unsigned
            //  16-bit values as in Apple's RGBColor data structure. Pure red = 65535, 0, 0.

            red = value1 / 256;
            green = value2 / 256;
            blue = value3 / 256;

            results.Add(Color.FromArgb(red, green, blue));
            break;

          case AdobePhotoshopColorSwatchColorSpace.Hsb:
            double hue;
            double saturation;
            double brightness;

            // HSB.
            // The first three values in the color data are hue , saturation , and brightness . They are full 
            // unsigned 16-bit values as in Apple's HSVColor data structure. Pure red = 0,65535, 65535.

            hue = value1 / 182.04;
            saturation = value2 / 655.35;
            brightness = value3 / 655.35;

            results.Add(new HslColor(hue, saturation, brightness).ToRgbColor());
            break;

          case AdobePhotoshopColorSwatchColorSpace.Grayscale:

            int gray;

            // Grayscale.
            // The first value in the color data is the gray value, from 0...10000.
            gray = (int)(value1 / 39.0625);

            results.Add(Color.FromArgb(gray, gray, gray));
            break;

          default:
            throw new InvalidDataException(string.Format("Color space '{0}' not supported.", colorSpace));
        }

#if USENAMEHACK
        results.SetName(i, name);
#endif
      }

      return results;
    }

    protected virtual void WritePalette(Stream stream, ColorCollection palette, AdobePhotoshopColorSwatchFileVersion version, AdobePhotoshopColorSwatchColorSpace colorSpace)
    {
      int swatchIndex;

      this.WriteInt16(stream, (short)version);
      this.WriteInt16(stream, (short)palette.Count);

      swatchIndex = 0;

      foreach (Color color in palette)
      {
        short value1;
        short value2;
        short value3;
        short value4;

        swatchIndex++;

        switch (colorSpace)
        {
          case AdobePhotoshopColorSwatchColorSpace.Rgb:
            value1 = (short)(color.R * 256);
            value2 = (short)(color.G * 256);
            value3 = (short)(color.B * 256);
            value4 = 0;
            break;
          case AdobePhotoshopColorSwatchColorSpace.Hsb:
            value1 = (short)(color.GetHue() * 182.04);
            value2 = (short)(color.GetSaturation() * 655.35);
            value3 = (short)(color.GetBrightness() * 655.35);
            value4 = 0;
            break;
          case AdobePhotoshopColorSwatchColorSpace.Grayscale:
            if (color.R == color.G && color.R == color.B)
            {
              // already grayscale
              value1 = (short)(color.R * 39.0625);
            }
            else
            {
              // color is not grayscale, convert
              value1 = (short)(((color.R + color.G + color.B) / 3.0) * 39.0625);
            }
            value2 = 0;
            value3 = 0;
            value4 = 0;
            break;
          default:
            throw new InvalidOperationException("Color space not supported.");
        }

        this.WriteInt16(stream, (short)colorSpace);
        this.WriteInt16(stream, value1);
        this.WriteInt16(stream, value2);
        this.WriteInt16(stream, value3);
        this.WriteInt16(stream, value4);

        if (version == AdobePhotoshopColorSwatchFileVersion.Version2)
        {
          string name;

#if USENAMEHACK
          name = palette.GetName(swatchIndex - 1);
          if (string.IsNullOrEmpty(name))
          {
            name = string.Format("Swatch {0}", swatchIndex);
          }
#else
          name = color.IsNamedColor ? color.Name : string.Format("Swatch {0}", swatchIndex);
#endif

          this.WriteInt32(stream, name.Length);
          this.WriteString(stream, name);
        }
      }
    }

    #endregion
  }
}
