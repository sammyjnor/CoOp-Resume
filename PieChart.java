import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.Group;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.shape.Arc;
import javafx.scene.shape.ArcType;
import javafx.scene.shape.Ellipse;
import javafx.scene.text.Font;
import javafx.stage.Stage;
import java.io.FileNotFoundException;
import java.util.*;
import java.io.*;
import java.util.Set;

public class PieChart extends Application
{
    
    public void start(Stage primaryStage)
    {
    
        File text = new File("C:/Users/15026/Documents/Summer CSE HW/daFile.txt");

        try {Scanner scan = new Scanner(text);
    
        String labela = scan.nextLine();
        String sa = scan.nextLine();
        String labelb = scan.nextLine();
        String sb = scan.nextLine();
        String labelc = scan.nextLine();
        String sc = scan.nextLine();
        String labeld = scan.nextLine();
        String sd = scan.nextLine();
        
        double a = Double.parseDouble(sa);
        double b = Double.parseDouble(sb);
        double c = Double.parseDouble(sc);
        double d = Double.parseDouble(sd);

        double total = (a+b+c+d);
        
        double pA = (a/total)*360;
        double pB = (b/total)*360;
        double pC = (c/total)*360;
        double pD = (d/total)*360;
        
        //To shorten the decimal values of the doubles, I elected to use
        //The Math.round() function. However, this method is not always the 
        //most accurate, and therefore, my percentages occasionally add up
        //to 99% or 101%. Considering this portion was extra credit, though,
        //I felt extra degrees of accuracy weren't necessary.
        
        String fullLa = labela + ": " + (Math.round(pA * (10.0/36.0))) + "%"; 
        String fullLb = labelb + ": " + (Math.round(pB * (10.0/36.0))) + "%"; 
        String fullLc = labelc + ": " + (Math.round(pC * (10.0/36.0))) + "%"; 
        String fullLd = labeld + ": " + (Math.round(pD * (10.0/36.0))) + "%"; 
        
        Text t1 = new Text(270, 100, fullLa);
        t1.setFont(Font.font ("Verdana", 20));
        t1.setFill(Color.LIGHTPINK);
        
        Text t2 = new Text(270, 120, fullLb);
        t2.setFont(Font.font ("Verdana", 20));
        t2.setFill(Color.THISTLE);
        
        Text t3 = new Text(270, 140, fullLc);
        t3.setFont(Font.font ("Verdana", 20));
        t3.setFill(Color.PALEVIOLETRED);
        
        Text t4 = new Text(270, 160, fullLd);
        t4.setFont(Font.font ("Verdana", 20));
        t4.setFill(Color.LIGHTSKYBLUE);
        
        Arc arc1 = new Arc(150, 150, 100, 100, 0, pA);
        arc1.setType(ArcType.ROUND);
        arc1.setStroke(Color.LIGHTPINK);
        arc1.setFill(Color.LIGHTPINK);
        
        Arc arc2 = new Arc(150, 150, 100, 100, pA, pB);
        arc2.setType(ArcType.ROUND);
        arc2.setStroke(Color.THISTLE);
        arc2.setFill(Color.THISTLE);
        
        Arc arc3 = new Arc(150, 150, 100, 100, (pA+pB), pC);
        arc3.setType(ArcType.ROUND);
        arc3.setStroke(Color.PALEVIOLETRED);
        arc3.setFill(Color.PALEVIOLETRED);
        
        Arc arc4 = new Arc(150, 150, 100, 100, (pA+pB+pC), pD);
        arc4.setType(ArcType.ROUND);
        arc4.setStroke(Color.LIGHTSKYBLUE);
        arc4.setFill(Color.LIGHTSKYBLUE);
        
        Group root = new Group(arc1, arc2, arc3, arc4, t1, t2, t3, t4);
        Scene scene = new Scene(root, 500, 300, Color.WHITE);
        
        primaryStage.setScene(scene);
        primaryStage.show();
    
    }
        catch(FileNotFoundException e){
            
            System.out.println("File not found!");
            return;
            
        }
        
    
       
}

}


