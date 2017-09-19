// 2015/10/14 - 20:49

using System;
using System.Windows.Forms;
using System.Drawing;

namespace Cyotek.Windows.Forms
{
    /// <summary>
    /// Class with program entry point.
    /// </summary>
    internal sealed class Program
    {
        /// <summary>
        /// Program entry point.
        /// </summary>
        [STAThread]
        private static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            var app = new Cyotek.Windows.Forms.ColorPickerDialog();
            
            if (args.Length > 0) {
                var incolor = args[0];
                System.Diagnostics.Debug.WriteLine("Inputing color: {0}", incolor);
                app.Color = ColorTranslator.FromHtml('#' + incolor.Substring(6, 2) + incolor.Substring(0, 6));
            } else {
                app.Color = Color.White;
            }
            
            Application.Run(app);
            
            var color = string.Format("#{0:X2}{1:X2}{2:X2}{3:X2}", app.Color.R, app.Color.G, app.Color.B, app.Color.A);
            
            Console.Write(app.DialogResult == DialogResult.OK ? color : "CANCEL");
            System.Diagnostics.Debug.WriteLine(color);
        }
        
    }
}
