"""Publication figures built from the new study, using ReportLab's chart engine."""
import csv
import json
import math
import statistics
from pathlib import Path
import pypdfium2
from reportlab.graphics import renderPDF,renderSVG
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing,String,Line,Circle,Rect
from reportlab.lib.colors import HexColor,Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .execution import ROOT
from .statistics import load_observations

LABELS={'uniform':'Ngẫu nhiên','ascending':'Tăng dần','descending':'Giảm dần',
    'almost_sorted':'Gần tăng dần','repeated_keys':'16 khóa lặp'}
COLORS=['#206b89','#32936f','#c16135','#a6841d','#7955a1']


def rows(path):
    with Path(path).open(encoding='utf-8') as handle: return list(csv.DictReader(handle))


def font():
    for name,path in [('Arial','/System/Library/Fonts/Supplemental/Arial.ttf'),
                      ('Arial','C:/Windows/Fonts/arial.ttf'),
                      ('DejaVuSans','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont(name,path));return name
    raise RuntimeError('A Vietnamese TrueType font is required to regenerate figures')


def label(drawing,text,x,y,size=10,color='#22313d',anchor='start',face='Arial'):
    drawing.add(String(x,y,text,fontName=face,fontSize=size,fillColor=HexColor(color),textAnchor=anchor))


def export(drawing,stem):
    target=ROOT/'report/charts'/stem
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary=ROOT/'scratch/chart-render';temporary.mkdir(parents=True,exist_ok=True)
    vector=temporary/(stem+'.pdf')
    renderPDF.drawToFile(drawing,str(vector))
    renderSVG.drawToFile(drawing,str(target.with_suffix('.svg')))
    with pypdfium2.PdfDocument(str(vector)) as pdf:
        pdf[0].render(scale=2.5).to_pil().save(target.with_suffix('.png'))


def line_chart(data,heading,limits,face,height=360):
    graphic=Drawing(720,height)
    chart=LinePlot()
    chart.x,chart.y,chart.width,chart.height=62,48,630,height-134
    chart.data=data;chart.joinedLines=1
    chart.xValueAxis.valueMin,chart.xValueAxis.valueMax=1,128
    chart.xValueAxis.valueSteps=[1,16,32,48,64,96,128]
    chart.xValueAxis.labelTextFormat=lambda value:str(int(value))
    chart.yValueAxis.valueMin,chart.yValueAxis.valueMax=limits
    spacing=.1 if limits[1]-limits[0]<.8 else .5
    chart.yValueAxis.valueSteps=[i*spacing for i in range(math.ceil(limits[0]/spacing),math.floor(limits[1]/spacing)+1)]
    chart.yValueAxis.labelTextFormat=lambda value:f'{value:.1f}'
    for axis in [chart.xValueAxis,chart.yValueAxis]:
        axis.labels.fontName=face;axis.labels.fontSize=9;axis.strokeColor=HexColor('#8c9ba6')
    chart.yValueAxis.visibleGrid=True
    chart.yValueAxis.gridStrokeColor=HexColor('#e0e6eb')
    chart.yValueAxis.gridStrokeWidth=.5
    graphic.add(chart)
    label(graphic,heading,62,height-23,12,face=face)
    label(graphic,'CUTOFF',378,10,10,anchor='middle',face=face)
    return graphic,chart


def build_figures():
    face=font()
    screen=ROOT/'measurements/screen'
    final=ROOT/'measurements/confirm'
    summary=json.loads((screen/'summary.json').read_text())
    confirmation=json.loads((final/'summary.json').read_text())
    points=rows(screen/'every-threshold.csv')
    representatives=sorted(summary['rankings'],key=lambda item:item['representative'])
    low=min(float(r['relative_time']) for r in points)
    high=max(float(r['relative_time']) for r in points)
    limits=(max(0,math.floor((low-.04)*10)/10),math.ceil((high+.04)*10)/10)
    graphic,chart=line_chart([
        [(int(r['cutoff']),float(r['relative_time'])) for r in points],
        [(r['representative'],r['score']) for r in representatives]],
        'Sàng lọc 69 CUTOFF trên dữ liệu mới',limits,face)
    chart.lines[0].strokeColor=HexColor('#abb9c3');chart.lines[0].strokeWidth=.9
    chart.lines[1].strokeColor=HexColor(COLORS[0]);chart.lines[1].strokeWidth=2
    label(graphic,'Thời gian chuẩn hóa theo C1   Xám: mọi ngưỡng   Xanh: đại diện cùng cây',62,305,9,face=face)
    export(graphic,'screening')
    effects=rows(screen/'distribution-effects.csv')
    lines=[[(int(r['cutoff']),float(r['relative_time'])) for r in effects if r['distribution']==family] for family in LABELS]
    values=[value for line in lines for _,value in line]
    graphic,chart=line_chart(lines,'Cùng thuật toán nhưng phân phối làm đổi hiệu năng',
        (max(0,math.floor((min(values)-.05)*2)/2),math.ceil((max(values)+.05)*2)/2),face,390)
    for index,(family,color) in enumerate(zip(LABELS,COLORS)):
        chart.lines[index].strokeColor=HexColor(color);chart.lines[index].strokeWidth=1.7
        xx,yy=62+(index%3)*215,337-(index//3)*16
        graphic.add(Line(xx,yy,xx+18,yy,strokeColor=HexColor(color),strokeWidth=2))
        label(graphic,LABELS[family],xx+24,yy-3,9,face=face)
    export(graphic,'input_distributions')
    selected=confirmation['selected_cutoff']
    comparisons=[e for e in confirmation['paired_effects'] if e['baseline']!=selected]
    graphic=Drawing(720,350)
    xmin=math.floor((min([1]+[e['ci_low'] for e in comparisons])-.025)*10)/10
    xmax=math.ceil((max([1]+[e['ci_high'] for e in comparisons])+.025)*10)/10
    xx=lambda value:145+(value-xmin)/(xmax-xmin)*400
    label(graphic,f'Pha xác nhận cuối với lựa chọn CUTOFF {selected} đã chốt',25,326,12,face=face)
    for tick in range(math.ceil(xmin*10),math.floor(xmax*10)+1):
        x=xx(tick/10)
        graphic.add(Line(x,45,x,290,strokeColor=HexColor('#e0e6eb'),strokeWidth=.6))
        label(graphic,f'{tick/10:.1f}',x,28,9,anchor='middle',face=face)
    graphic.add(Line(xx(1),45,xx(1),290,strokeColor=HexColor('#637887'),strokeDashArray=[3,3]))
    for index,effect in enumerate(comparisons):
        yy=270-index*35
        left,right,center=map(xx,[effect['ci_low'],effect['ci_high'],effect['speedup']])
        label(graphic,f'Mốc C{effect["baseline"]}',25,yy-3,10,face=face)
        graphic.add(Line(left,yy,right,yy,strokeColor=HexColor(COLORS[0]),strokeWidth=2))
        for x in [left,right]: graphic.add(Line(x,yy-4,x,yy+4,strokeColor=HexColor(COLORS[0])))
        graphic.add(Circle(center,yy,3.5,fillColor=HexColor(COLORS[0]),strokeColor=None))
        label(graphic,f'{effect["speedup"]:.4f}×',568,yy-3,10,face=face)
    label(graphic,'Speedup = thời gian mốc / thời gian lựa chọn; thanh là khoảng bootstrap 95%',360,8,9,anchor='middle',face=face)
    export(graphic,'final_intervals')
    configuration,_,medians=load_observations(final)
    graphic=Drawing(720,310)
    label(graphic,f'Speedup của C{selected} trước C10 theo từng phân phối và kích thước',25,286,12,face=face)
    for column,n in enumerate(configuration['lengths']):
        label(graphic,f'N = {n:,}',215+column*125,251,9,anchor='middle',face=face)
    for row,family in enumerate(configuration['families']):
        label(graphic,LABELS[family],25,214-row*39,10,face=face)
        for column,n in enumerate(configuration['lengths']):
            logs=[math.log(medians[(family,n,s,f,10)]/medians[(family,n,s,f,selected)])
                for s in configuration['seeds'] for f in range(configuration['processes'])]
            speed=math.exp(statistics.fmean(logs))
            strength=min(1,abs(math.log(speed))/.3)
            base=(.13,.43,.54) if speed>=1 else (.76,.35,.21)
            color=Color(*(1-(1-component)*(.12+.65*strength) for component in base))
            graphic.add(Rect(155+column*125,201-row*39,120,33,fillColor=color,strokeColor=HexColor('#ffffff')))
            label(graphic,f'{speed:.3f}×',215+column*125,212-row*39,11,anchor='middle',face=face)
    label(graphic,'Xanh: nhanh hơn C10   Cam: chậm hơn C10   Không thay trọng số tổng hợp',25,16,9,face=face)
    export(graphic,'condition_sensitivity')
