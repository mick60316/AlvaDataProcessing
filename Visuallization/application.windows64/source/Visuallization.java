import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class Visuallization extends PApplet {

Table argvTable;
Table table;
DataBuffer []db;
HashMap <String, Integer> map =new HashMap<String, Integer>();

int [] c =new int[5];
int count;

int totalSecond;

int startHour =0;
int startMinute=0;
int startPos=1000;
int endPos=30000;
int sampleRate=1;
String inputFile="tagData.csv";
String outFile="img";

PImage backgroundImage;
public void setup() {
  backgroundImage=loadImage("background.png");
  background(backgroundImage);

  
  c[0] = color(237, 125, 49);
  c[1] = color(162, 229, 194);
  c[2] = color(165, 198, 228);
  c[3] = color(143, 121, 235);
  c[4] = color(127, 127, 127);


  map.put ("awake", 0);
  map.put ("Move Around", 1);
  map.put ("Asleep", 2);
  map.put ("About to wake", 3);
  map.put ("AWAY", 4);

  argvTable=loadTable("argument.csv", "header");
  for (TableRow row : argvTable.rows()) {

    startHour= row.getInt("Start Hour");
    startMinute=row.getInt("Start Minute");
    startPos=row.getInt("Start Pos");
    endPos=row.getInt("End Pos");

    sampleRate=row.getInt("Sample Rate");
    inputFile=row.getString("Input File");
    outFile=row.getString("Ouput File");
  }

  table = loadTable(inputFile, "header");

  count =table.getRowCount();
  db =new DataBuffer[count];

  int index= 0;
  for (TableRow row : table.rows()) {
    String MPI = row.getString("MPI tag");
    String MLI = row.getString("MLI tag");
    db[index] =new DataBuffer(MPI, MLI);
    //println (index+" "+MPI+" "+ map.get(MPI) +" "+MLI);
    index++;
  }
  if (endPos ==-1)
  {
    endPos=db.length;
  }


  drawBackground();
  drawForeground();
}
public void drawForeground()
{
  int posCount =0;
  int index= 0;
  int lineStartPos =startPos;
  int lineEndPos;
  for (int i =startPos; i<endPos; i+=sampleRate)
  {
    if (map.containsKey(db[i].MPI))
    {
      int type = map.get(db[i].MPI);
      stroke (c[type]);
    } else
    {
      stroke(0, 0, 0);
    }
    line(posCount, 500, posCount, 700);
    if (db[i].getMLI().equals("Kick"))
    {

      fill(255, 192, 0);
      stroke(0, 0, 0);
      noStroke();
      circle(posCount-5, 710, 4);
    }


    posCount++;
    if (posCount==1919)
    {
      posCount = 0;
      index++;
      lineEndPos =i;
      stroke(255, 0, 0);

      int pos1 =(int)((float)(lineStartPos*1920.0f/count));
      int pos2 =(int)((float)(lineEndPos*1920.0f/count));

      fill(255, 0, 0);
      rect(pos1, 175, pos2-pos1, 50);
      fill(255);

      stroke(255);
      line(0, 750, 1920, 750);
      for (int j =0; j<10; j++)
      {
        String time =secondToTimeString(lineStartPos/3+startHour*3600+startMinute*60+j*((lineEndPos-lineStartPos)/3)/10);
        text(time, j*1920/10-10, 850);
        line(j*1920/10, 700, j*1920/10, 800);
      }
      line(1919, 700, 1919, 800);
      save(outFile+"_"+lineStartPos+"_"+i+".jpg");
      lineStartPos =lineEndPos;
      drawBackground();
    }
  }
}
public void drawBackground ()
{
  background(backgroundImage);
  for (int i=0; i<count; i+=1)
  {
    float currentI=i;
    float posX =(float) (currentI /count) *1920;

    if (map.containsKey(db[i].MPI))
    {
      int type = map.get(db[i].MPI);
      stroke (c[type]);
    } else
    {
      stroke(0, 0, 0);
    }

    line(posX, 0, posX, 150);
    if (db[i].getMLI().equals("Kick"))
    {

      fill(255, 192, 0);
      stroke(0, 0, 0);
      noStroke();
      circle(posX-5, 160, 4);
    }
  }

  stroke(255, 255, 255);
  fill(255, 255, 255);

  textSize (32);
  int startSecond=startHour*3600+startMinute*60;
  totalSecond =count/3+startSecond;
  String startTimeStr =secondToTimeString(startSecond);
  String endTimeStr=secondToTimeString(totalSecond);
  line(0, 200, 1920, 200);
  for (int i =0; i<10; i++)
  {
    String time =secondToTimeString(startSecond+i*(totalSecond-startSecond)/10);
    text(time, i*1920/10-10, 300);
    line(i*1920/10, 150, i*1920/10, 250);
  }
  line(1919, 150, 1919, 250);
  text(secondToTimeString(totalSecond), 1820, 300);
}

public String secondToTimeString (int second)
{
  int s =second%60;
  second -=s;
  second/=60;
  int m =second%60;
  second-=m;
  second/=60;
  int h=second;
  return String.format("%d:%02d", h, m);
}
public void draw ()
{
}
class DataBuffer {
  public String MPI;
  public String MLI;
  public DataBuffer (String MPI,String MLI)
  {
    this.MPI =MPI;
    this.MLI=MLI;
  }
  
  public String getMPI ()
  {
    return MPI;
  }
  public String getMLI ()
  {
    return MLI;
  
  }
  
}
  public void settings() {  size (1920, 1080); }
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "Visuallization" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
