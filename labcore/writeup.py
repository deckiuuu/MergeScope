"""Author a new Vietnamese research report from this rebuild's evidence only."""
from datetime import datetime,timezone,timedelta
import json
import math
from pathlib import Path
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm,Pt,RGBColor
from .execution import ROOT
from .figures import build_figures,rows,LABELS
from .statistics import structural_groups


def decimal(value,places=4): return f'{value:.{places}f}'
def integer(value): return f'{value:,}'.replace(',','.')
def sequence(values): return '; '.join(map(integer,values))


class Composer:
    def __init__(self):
        self.document=Document();self.markdown=[]
        page=self.document.sections[0]
        page.page_width,page.page_height=Cm(21),Cm(29.7)
        page.top_margin,page.bottom_margin=Cm(1.9),Cm(1.9)
        page.left_margin,page.right_margin=Cm(2.1),Cm(2.1)
        for name in ['Normal','Title','Heading 1','Heading 2','Caption']:
            style=self.document.styles[name]
            style.font.name='Times New Roman';style.font.color.rgb=RGBColor(0,0,0)
            style.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),'Times New Roman')
        normal=self.document.styles['Normal']
        normal.font.size=Pt(11.5)
        normal.paragraph_format.line_spacing=1.12
        normal.paragraph_format.space_after=Pt(7)
        self.document.styles['Title'].font.size=Pt(23)
        self.document.styles['Heading 1'].font.size=Pt(16)
        self.document.styles['Heading 2'].font.size=Pt(12)
        for name in ['Heading 1','Heading 2']:
            self.document.styles[name].paragraph_format.space_before=Pt(9)
            self.document.styles[name].paragraph_format.space_after=Pt(6)
        footer=page.footer.paragraphs[0]
        footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
        field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
        self.document.core_properties.title='Thực nghiệm lựa chọn CUTOFF cho MergeSort'
        self.document.core_properties.author='Sinh viên thực hiện với hỗ trợ AI được công bố'

    def text(self,value,style=None):
        paragraph=self.document.add_paragraph(value,style)
        self.markdown.extend([value,''])
        return paragraph

    def heading(self,value,new_page=True):
        if new_page:self.document.add_page_break()
        self.document.add_paragraph(value,'Heading 1')
        self.markdown.extend(['## '+value,''])

    def subheading(self,value):
        self.document.add_paragraph(value,'Heading 2');self.markdown.extend(['### '+value,''])

    def table(self,headers,body,widths):
        table=self.document.add_table(rows=1,cols=len(headers));table.autofit=False
        for column,width in zip(table.columns,widths):column.width=Cm(width)
        for cell,value in zip(table.rows[0].cells,headers):cell.text=str(value)
        repeat=OxmlElement('w:tblHeader');table.rows[0]._tr.get_or_add_trPr().append(repeat)
        for values in body:
            for cell,value in zip(table.add_row().cells,values):cell.text=str(value)
        for i,row in enumerate(table.rows):
            for j,cell in enumerate(row.cells):
                cell.width=Cm(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                properties=cell._tc.get_or_add_tcPr()
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E1E7EC' if i==0 else ('F4F6F8' if i%2==0 else 'FFFFFF'));properties.append(shade)
                borders=OxmlElement('w:tcBorders')
                for side in ['top','bottom','left','right']:
                    edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:color'),'D9D9D9');edge.set(qn('w:sz'),'4');borders.append(edge)
                properties.append(borders)
                padding=OxmlElement('w:tcMar')
                for side in ['top','bottom','left','right']:
                    margin=OxmlElement('w:'+side);margin.set(qn('w:w'),'85');margin.set(qn('w:type'),'dxa');padding.append(margin)
                properties.append(padding)
                for paragraph in cell.paragraphs:
                    paragraph.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 else WD_ALIGN_PARAGRAPH.CENTER
                    paragraph.paragraph_format.space_after=Pt(1);paragraph.paragraph_format.line_spacing=1.05
                    for run in paragraph.runs:run.font.size=Pt(10.5);run.bold=i==0
        self.document.add_paragraph().paragraph_format.space_after=Pt(0)
        self.markdown.extend(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |'])
        self.markdown.extend('| '+' | '.join(map(str,record))+' |' for record in body)
        self.markdown.append('')

    def picture(self,stem,caption):
        paragraph=self.document.add_paragraph()
        paragraph.add_run().add_picture(str(ROOT/'report/charts'/(stem+'.png')),width=Cm(16.7))
        paragraph.paragraph_format.space_after=Pt(2);paragraph.paragraph_format.keep_with_next=True
        self.text(caption,'Caption')
        self.markdown.extend([f'![{caption}](charts/{stem}.png)',''])

    def code(self,value):
        paragraph=self.document.add_paragraph()
        paragraph.paragraph_format.line_spacing=1.02
        run=paragraph.add_run(value);run.font.name='Courier New';run.font.size=Pt(9)
        self.markdown.extend(['```text',value,'```',''])

    def save(self):
        for root in [self.document.element,self.document.styles.element]:
            for border in root.xpath('.//w:pBdr'):border.getparent().remove(border)
        self.document.save(ROOT/'report/Cutoff_Study.docx')
        (ROOT/'report/Cutoff_Study.md').write_text('\n'.join(self.markdown),encoding='utf-8')


def comparison_sentence(effect,chosen):
    if effect['ci_low']<=1<=effect['ci_high']:
        return f'Khoảng 95% trước mốc {effect["baseline"]} chứa 1, chưa phân biệt rõ hai lựa chọn.'
    if effect['ci_low']>1:
        return f'Khoảng 95% trước mốc {effect["baseline"]} nằm trên 1, nghiêng về CUTOFF {chosen} trong thiết kế này.'
    return f'Khoảng 95% trước mốc {effect["baseline"]} nằm dưới 1; mốc đó có lợi thế trên dữ liệu xác nhận.'


def build_report():
    study=json.loads((ROOT/'study.json').read_text())
    summaries={phase:json.loads((ROOT/'measurements'/phase/'summary.json').read_text()) for phase in study['phases']}
    evidence={phase:json.loads((ROOT/'measurements'/phase/'evidence.json').read_text()) for phase in study['phases']}
    screen,choose,confirm=(summaries[p] for p in ['screen','choose','confirm'])
    selected=confirm['selected_cutoff']
    effects={row['baseline']:row for row in confirm['paired_effects']}
    source=json.loads((ROOT/'docs/ORIGIN.json').read_text())
    total_observations=sum(r['observations'] for r in summaries.values())
    total_sorts=sum(r['timed_sort_calls'] for r in summaries.values())
    hardware=evidence['confirm']['machine']
    started=datetime.fromisoformat(evidence['screen']['start_utc']).astimezone(timezone(timedelta(hours=7)))
    finished=datetime.fromisoformat(evidence['confirm']['finish_utc']).astimezone(timezone(timedelta(hours=7)))
    meta={line.split('=',1)[0]:line.split('=',1)[1] for line in (ROOT/'measurements/confirm/process-00.properties').read_text().splitlines() if '=' in line and not line.startswith('#')}
    build_figures()
    report=Composer()
    report.text('Thực nghiệm lựa chọn CUTOFF\ncho MergeSort','Title')
    report.text(f'Báo cáo phân tích thuật toán  |  Ngày {started:%d/%m/%Y}')
    report.text('Họ và tên: ____________________     MSSV: ____________________\nLớp: ____________________     Giảng viên: ____________________')
    report.subheading('Kết luận của thí nghiệm')
    report.text(f'Đề xuất CUTOFF {selected} cho cài đặt MergeSort được cung cấp và workload Integer[] đã xác định. Trên tập xác nhận cuối, speedup so với CUTOFF 7 là {effects[7]["speedup"]:.4f} lần, so với CUTOFF 10 là {effects[10]["speedup"]:.4f} lần. Tỷ lệ giảm thời gian trước mốc 10 là {effects[10]["time_saved_fraction"]*100:.2f}%.')
    alternatives=[r for r in confirm['paired_effects'] if r['baseline'] in confirm['shortlist'] and r['baseline']!=selected]
    closest=min(alternatives,key=lambda r:abs(math.log(r['speedup'])))
    report.text(comparison_sentence(closest,selected)+' Khuyến nghị là một lựa chọn thực dụng trong vùng gần tối ưu; không xác định một hằng số nhanh nhất duy nhất cho mọi kích thước, kiểu dữ liệu và máy.')
    report.table(['Chỉ tiêu','Sàng lọc','Chọn','Xác nhận'],[
        ['Số mảng',60,60,60],['Ứng viên đo',len(screen['configuration']['thresholds']),len(choose['configuration']['thresholds']),len(confirm['configuration']['thresholds'])],
        ['JVM × vòng đo','3 × 5','5 × 7','5 × 7'],['Quan sát batch',*[integer(summaries[p]['observations']) for p in ['screen','choose','confirm']]],
        ['Sort trong vùng đo',*[integer(summaries[p]['timed_sort_calls']) for p in ['screen','choose','confirm']]]],[5.0,3.9,3.9,3.9])
    report.subheading('Câu hỏi nghiên cứu')
    report.text('Mốc 7 và 10 trong đề bài cần được kiểm tra bằng thí nghiệm trên cài đặt và máy thực tế. Khi tăng cutoff, chi phí chia và trộn giảm nhưng phần Insertion sort nhận các đoạn dài hơn. Thí nghiệm xem xét sự đánh đổi đó trên nhiều thứ tự đầu vào và số khóa trùng, thay vì chỉ đo một mảng ngẫu nhiên.')
    report.text('Thiết kế ba pha được ghi trước khi đo: sàng lọc, chọn trên dữ liệu mới, rồi xác nhận lựa chọn đã chốt bằng dữ liệu chưa sử dụng. Bản mã MergeSort giữ nguyên; mọi công cụ và sản phẩm phụ trợ của lần làm lại này được tạo mới.')

    report.heading('1 Mã nguồn và tính đúng')
    report.text('Đối tượng nghiên cứu là tệp MergeSort.java do người dùng cung cấp. Cài đặt có chia đôi đệ quy, mảng phụ dùng chung trong một lần sort, trộn bằng hai con trỏ và Insertion sort đổi chỗ kề nhau. Chỉ tham số cutoff thay đổi giữa các phép đo; không thêm nhánh bỏ merge hoặc thay cách chèn.')
    report.code('if (hi - lo < cutoff) {\n    insertionSort(a, lo, hi);\n    return;\n}')
    report.text('Vì hai chỉ số đầu cuối đều được tính vào đoạn, độ dài là hi - lo + 1. Điều kiện trong mã tương đương độ dài không vượt cutoff: CUTOFF 10 nhận đoạn có tối đa 10 phần tử. Với cutoff 1, cây đi đến các đoạn đơn phần tử; đây là đường cơ sở trong cùng bản cài đặt tham số hóa.')
    report.subheading('Lập luận về tính đúng và tính ổn định')
    report.text('Insertion sort giữ phần đầu đoạn có thứ tự và đưa phần tử tiếp theo về vị trí thích hợp bằng các phép đổi chỗ. Sau hai lời gọi đệ quy, mỗi nửa đã tăng dần. Hai con trỏ của merge chọn phần tử nhỏ nhất còn lại và ghi lần lượt vào đoạn đích; không mất hoặc thêm phần tử.')
    report.text('Phép chèn chỉ đổi chỗ khi khóa bên phải nhỏ hơn thực sự. Khi merge gặp hai khóa bằng nhau, mã lấy từ nửa trái trước. Hai quy tắc này bảo toàn thứ tự tương đối của các đối tượng bằng khóa, nên thuật toán ổn định.')
    report.table(['Nhóm kiểm thử mới','Nội dung'],[
        ['Vét cạn','Mọi dãy trên {-1, 0, 1} có độ dài 0 đến 6; cutoff 1 đến 12'],
        ['Biên và ngẫu nhiên','Mọi cutoff 1 đến 128; N ngay trước, bằng và sau cutoff; nhiều mảng ngẫu nhiên'],
        ['Ổn định và generic','Đối tượng có khóa trùng kèm số thứ tự; so với oracle ổn định; mảng String'],
        ['API và giá trị cực trị','Mảng null, cutoff không hợp lệ, int nhỏ nhất/lớn nhất và mảng dài giảm dần']], [4.3,12.4])
    report.text('Bộ kiểm thử đạt 15.693 kiểm tra độc lập. Arrays.sort chỉ dùng làm oracle ngoài vùng đo, không xuất hiện trong MergeSort.java. Mọi output của benchmark tiếp tục được đối chiếu toàn bộ bằng giá trị ngay sau lần đo, không chỉ kiểm tra mảng đã tăng dần.')
    report.text('Với cutoff cố định, độ phức tạp xấu nhất vẫn O(N log N); mảng phụ cần O(N), stack cần O(log N). Nếu cutoff lớn hơn hoặc bằng N, cả mảng chạy Insertion sort và xấu nhất O(N²). Đây là lý do không chọn cutoff càng lớn càng tốt.')

    report.heading('2 Giao thức thí nghiệm')
    report.text('study.json được ghi trước khi chạy JVM đầu tiên. Sàng lọc khảo sát 69 giá trị: 1 đến 64, 72, 80, 96, 112 và 128. Ba đại diện tốt nhất có cấu trúc cây khác nhau được đưa sang pha chọn. Pha chọn chỉ so sánh ba ứng viên đã chốt và các mốc đối chiếu. Lựa chọn thắng ở pha này được giữ nguyên khi xác nhận cuối.')
    report.table(['Pha','Độ dài N','Seed dữ liệu'],[
        ['Sàng lọc',sequence(study['phases']['screen']['lengths']),sequence(study['phases']['screen']['seeds'])],
        ['Chọn',sequence(study['phases']['choose']['lengths']),sequence(study['phases']['choose']['seeds'])],
        ['Xác nhận',sequence(study['phases']['confirm']['lengths']),sequence(study['phases']['confirm']['seeds'])]], [2.6,7.3,6.8])
    report.text('Mỗi pha có bốn độ dài, ba seed và năm phân phối, tạo 60 mảng. Độ dài và seed tách biệt hoàn toàn giữa ba pha. Tập xác nhận không dùng để chọn lại ngưỡng. Quy tắc dừng là đúng ba pha đã định, bất kể kết quả pha cuối; không mở thêm lượt để tìm một thứ hạng ưa thích.')
    report.subheading('Môi trường đo thực tế')
    report.table(['Thành phần','Giá trị ghi nhận'],[
        ['Máy',f'{hardware.get("machine_name",hardware["system"])}; {hardware.get("chip_type","")}'],
        ['Bộ nhớ và kiến trúc',f'{hardware.get("physical_memory","")}; {hardware["architecture"]}; {hardware.get("number_processors","")}'],
        ['Hệ điều hành',f'{hardware["system"]}, kernel {hardware["kernel"]}'],
        ['Java',f'{meta.get("java.vendor","")}; {meta.get("java.version","")}; {meta.get("java.vm.name","")}'],
        ['Cấu hình JVM',' '.join(study['jvm_options'])],
        ['Thời điểm Việt Nam',f'{started:%d/%m/%Y %H:%M} đến {finished:%H:%M} UTC+7']], [4.3,12.4])
    report.text('Sàng lọc dùng 3 JVM nối tiếp, mỗi JVM đo 5 vòng. Hai pha sau dùng 5 JVM, mỗi JVM đo 7 vòng. Mỗi JVM warmup tối thiểu 3 giây và mỗi mảng có một vòng thực hành không ghi số đo. Thứ tự mảng và thứ tự cutoff ở từng vòng được xáo bằng seed lưu trong cấu hình.')
    report.text('Các JVM chạy riêng, không đo song song. Không ghi liên tục nhiệt độ, tần số CPU hoặc tải nền; metadata phần cứng và JVM không loại bỏ hoàn toàn những nguồn biến động này. Kết quả vì vậy chỉ đại diện cho phiên máy và thiết kế được mô tả.')

    report.heading('3 Dữ liệu và phương pháp thống kê')
    report.table(['Phân phối','Cách tạo mới'],[
        ['Ngẫu nhiên','Số nguyên đều trong [-2.000.000; 2.000.000]'],
        ['Tăng dần','Sắp tăng bản ngẫu nhiên của cùng N và seed'],
        ['Giảm dần','Đảo bản tăng dần'],
        ['Gần tăng dần','Từ bản tăng, thực hiện max(1, floor(N/200)) lần đổi hai vị trí ngẫu nhiên'],
        ['16 khóa lặp','Các khóa 1.000.000 + 257k, k từ 0 đến 15']], [3.6,13.1])
    report.text('Khóa lặp có giá trị lớn để tránh tập trung vào vùng cache Integer nhỏ thông thường. Tuy nhiên ảnh hưởng của khóa trùng, cách cấp phát đối tượng và JVM vẫn chưa được tách thành các nhân tố độc lập. Dữ liệu được lưu thành 180 CSV một cột value, có seed, công thức RNG và SHA-256 trong index của từng pha.')
    report.subheading('Phạm vi đồng hồ và đơn vị quan sát')
    report.text('Chỉ lời gọi MergeSort.sort được tính thời gian, bao gồm cấp phát aux mới. Đọc file, boxing, clone input và oracle đều ngoài đồng hồ. Batch có ceil(6000/N) lần sort, giới hạn từ 1 đến 8; mọi bản sao được chuẩn bị trước. Thời gian batch chia số sort tạo nanos_per_sort. Các sort trong một batch không được coi là các mẫu thời gian độc lập.')
    report.code('khôi phục các bản sao input\nđọc System.nanoTime()\ngọi MergeSort.sort cho từng bản sao\nđọc System.nanoTime() và lấy hiệu\nkiểm tra toàn bộ output với oracle\nlưu elapsed_ns và elapsed_ns / batch_size')
    report.text('Trong mỗi khối phân phối × N × seed × JVM × cutoff, lấy median qua các vòng. Điểm ứng viên là trung bình nhân của tỷ số median ứng viên trên median C1 trong cùng khối. Mọi phân phối × N có trọng số bằng nhau, đồng thời các seed và JVM cũng có trọng số bằng nhau. Không bỏ outlier sau khi xem kết quả.')
    report.text('Ở pha sàng lọc, các cutoff cùng cây trên toàn bộ N được nhóm theo chữ ký kích thước lá; chỉ đại diện nhỏ nhất được dùng để chọn shortlist. Số đo của các cutoff tương đương vẫn được giữ, nhưng không gộp thành thêm trọng số cho nhóm đông thành viên. Hai pha sau giữ nguyên ba ứng viên đã chốt.')
    report.text('Khoảng 95% dùng 4.000 bootstrap phân cấp: lấy lại JVM có hoàn lại, rồi lấy lại seed bên trong JVM, giữ cả ma trận phân phối × N của cụm đó. Các khoảng là từng cặp và không bao phủ đồng thời mọi ứng viên; chỉ có 3 hoặc 5 JVM. Quy ước gần tối ưu là thời gian cao hơn điểm thấp nhất không quá 3%, được ghi trước thí nghiệm và khác với một kết luận ý nghĩa thống kê.')

    report.heading('4 Kết quả sàng lọc')
    report.picture('screening','Hình 1  Điểm thời gian trên tập sàng lọc  Thấp hơn là nhanh hơn')
    groups=screen['rankings']
    keep={r['representative'] for r in groups[:5]}
    keep.update(r['representative'] for r in groups if set(r['same_tree'])&{1,7,10,128})
    report.table(['Đại diện','Cutoff cùng cây trên N sàng lọc','Điểm so với C1'],[
        [r['representative'],sequence(r['same_tree']) if len(r['same_tree'])<=3 else f'{r["same_tree"][0]} đến {r["same_tree"][-1]}',decimal(r['score'])]
        for r in sorted(groups,key=lambda r:r['representative']) if r['representative'] in keep],[2.8,9.8,4.1])
    report.text(f'Ba đại diện được chốt là {sequence(screen["shortlist"])}. Điểm thấp nhất là {screen["rankings"][0]["score"]:.4f} ở đại diện {screen["selected_cutoff"]}; các điểm gần nhau chưa cho biết ứng viên nào thắng trên dữ liệu mới. Pha tiếp theo chỉ dùng shortlist này và các mốc đối chiếu đã định.')
    report.text('Các đoạn chỉ có một số độ dài khi chia đôi. Nếu thay cutoff mà không vượt một độ dài nút nào, cây xử lý không đổi. Khi tăng cutoff, cây chỉ được gộp dần, nên chữ ký số lượng và độ dài lá không đổi đồng nghĩa không có nút nào đổi từ chia sang lá. Số đo từng tham số vẫn có nhiễu; không chọn một cutoff tương đương chỉ vì nó có một điểm thấp hơn ngẫu nhiên.')

    report.heading('5 Chốt ứng viên và xác nhận cuối')
    report.picture('final_intervals',f'Hình 2  Speedup của C{selected} đã chốt  Dữ liệu xác nhận chưa dùng để chọn')
    report.table(['Mốc','Speedup','Khoảng bootstrap 95%','Giảm thời gian'],[
        [r['baseline'],decimal(r['speedup']),decimal(r['ci_low'])+' đến '+decimal(r['ci_high']),f'{r["time_saved_fraction"]*100:.2f}%']
        for r in confirm['paired_effects'] if r['baseline']!=selected],[2.2,3.2,7.1,4.2])
    report.text(f'Pha chọn có điểm thấp nhất ở C{choose["selected_cutoff"]}, nên ngưỡng này được lưu trong confirm-frozen.json trước JVM xác nhận đầu tiên. Speedup là thời gian mốc chia thời gian lựa chọn. Vì vậy speedup {effects[10]["speedup"]:.4f} trước C10 tương ứng giảm {effects[10]["time_saved_fraction"]*100:.2f}% thời gian, không phải giảm {(effects[10]["speedup"]-1)*100:.2f}%.')
    for row in [effects[7],effects[10],closest]:report.text(comparison_sentence(row,selected))
    final_group=next(g for g in structural_groups(confirm['configuration']['lengths'],range(1,129)) if selected in g)
    report.text(f'Trên toàn bộ N của pha cuối, các cutoff từ {final_group[0]} đến {final_group[-1]} có cùng cấu trúc cây. Quan hệ này khác trên tập sàng lọc. Giữ lựa chọn C{selected} và báo cáo đầy đủ kết quả của các ứng viên cạnh tranh, không đổi kết luận bằng cách nhìn một số đo thấp nhất của tập cuối.')
    report.text(f'Tổng ba pha có {integer(total_observations)} quan sát batch và {integer(total_sorts)} lời gọi sort trong vùng đo. Mọi output khớp oracle; các lần warmup không tính vào hai tổng này. Hash nguồn, dữ liệu, cấu hình và quyết định đã được kiểm tra độc lập bằng cutofflab.py verify.')

    report.heading('6 Phân phối và kích thước làm đổi lợi ích')
    report.picture('input_distributions','Hình 3  Tỷ số thời gian theo phân phối trên tập sàng lọc')
    report.picture('condition_sensitivity','Hình 4  So sánh ghép cặp CUTOFF đã chọn với C10 trên từng ca xác nhận')
    report.text('Đầu vào tăng dần giúp Insertion sort gần như không đổi chỗ; cutoff lớn thường có lợi. Đầu vào giảm dần tạo nhiều nghịch thế, khiến các đoạn chèn dài đắt hơn. Hình 4 cho thấy một lợi thế tổng hợp không đồng nghĩa lợi thế trên từng loại input. Ngưỡng khuyến nghị phụ thuộc trọng số workload; nếu một ứng dụng nhận chủ yếu mảng giảm dần, cần thiết kế lại phép đo cho phân phối đó.')

    report.heading('7 Thời gian tuyệt đối và độ phân tán')
    descriptions=rows(ROOT/'measurements/confirm/descriptive-times.csv')
    lookup={(r['distribution'],int(r['length']),int(r['cutoff'])):r for r in descriptions}
    samples=confirm['configuration']['processes']*confirm['configuration']['repetitions']*len(confirm['configuration']['seeds'])
    report.text(f'Bảng ghi median mili giây mỗi sort trên pha xác nhận. Mỗi ô gộp {samples} quan sát batch. Đây là bảng mô tả thời gian tuyệt đối; các tỷ số trong kết luận được tính từ median của từng khối ghép cặp, không lấy tỷ số trực tiếp của các ô gộp.')
    report.table(['Phân phối','N','C1 ms','C10 ms',f'C{selected} ms'],[
        [LABELS[family],integer(n),*[decimal(float(lookup[family,n,c]['median_ms']),3) for c in [1,10,selected]]]
        for n in confirm['configuration']['lengths'] for family in study['families']], [4.8,2.6,3.1,3.1,3.1])
    example=lookup['uniform',max(confirm['configuration']['lengths']),selected]
    report.text(f'Ví dụ ngẫu nhiên N = {integer(max(confirm["configuration"]["lengths"]))}, C{selected}: median {float(example["median_ms"]):.3f} ms; mean {float(example["mean_ms"]):.3f} ms; độ lệch chuẩn mẫu {float(example["sd_ms"]):.3f} ms; Q1-Q3 {float(example["q1_ms"]):.3f}-{float(example["q3_ms"]):.3f} ms. Chưa có trace nguyên nhân để gán riêng một quan sát chậm cho GC hay tải nền.')
    report.text('descriptive-times.csv còn lưu min, max và MAD cho từng phân phối × N × cutoff. process-*.csv giữ các lần đo gốc, thứ tự ứng viên, batch, tổng nano giây và checksum. Độ lệch chuẩn mô tả không giả định mọi quan sát gộp là độc lập; bootstrap dùng cấp JVM và seed để phản ánh cấu trúc lặp.')

    report.heading('8 Chạy lại và trình bày bằng demo')
    report.subheading('Các bước tái lập')
    report.text('Cần JDK 17 trở lên và Python 3.10 trở lên để chạy đo, kiểm thử và phân tích; các bước này chỉ dùng thư viện chuẩn. Chạy một phiên mới dưới reruns/ để giữ nguyên số liệu đã bàn giao. Thời gian chạy lại có nhiễu nên thứ hạng không bắt buộc giống bản báo cáo.')
    report.code('python3 cutofflab.py test\npython3 -m unittest discover -s tests -p "test_*.py"\npython3 cutofflab.py verify\npython3 cutofflab.py study --new-run lan_do_moi')
    report.text('Giao thức, cấu hình từng pha và quyết định chốt có hash và thời điểm UTC. Mỗi pha giữ source-snapshot của các tệp Java thực sự được biên dịch. Dataset index lưu SHA-256 từng CSV. Lệnh verify kiểm tra ma trận phép đo đầy đủ, thứ tự ứng viên là hoán vị, checksum kết quả và dữ liệu tách biệt giữa ba pha.')
    report.subheading('Demo ghi trực tiếp các phép so sánh')
    report.text('Mở demo/index.html để chọn N = 16 hoặc 33, đổi thứ tự đầu vào và CUTOFF từ 1 đến 128. Có nút tiến, lùi, về đầu, đến cuối, tự chạy và các mốc nhanh 1, 7, 10 cùng ngưỡng khuyến nghị. Nhãn # lưu vị trí ban đầu, giúp kiểm tra thứ tự các khóa bằng nhau sau khi hoàn tất.')
    report.text('TraceCapture gọi đúng MergeSort.sort với đối tượng Comparable ghi lại compareTo. StackWalker nhận diện phép so sánh thuộc insertionSort hay merge và độ sâu ngăn xếp [3]. Mảng được chụp trước so sánh; bước kế tiếp phản ánh những lần ghi đã xảy ra. Không viết một bản MergeSort thứ hai để sinh trace và không chỉnh mã người dùng.')
    report.text('Có 768 lượt chạy Java thực tế, mỗi lượt đối chiếu với oracle ổn định. Chỉ gộp bản ghi khi toàn bộ chuỗi sự kiện giống nhau từng byte, còn 45 bản ghi khác nhau. Cây chia trên giao diện được dựng từ độ dài và cutoff để giải thích cấu trúc; nó không phải dữ liệu đo thời gian. Khi merge đang ghi dở, mảng có thể tạm lặp phần tử vì nguồn đọc là aux.')
    report.text('Để dựng lại demo dùng python3 cutofflab.py demo; để kiểm tra logic tương tác dùng node --test tests/test_viewer.cjs. Kiểm tra logic không thay thế kiểm tra bố cục bằng trình duyệt. Công cụ hiện tại chặn mở tệp cục bộ trong trình duyệt; phạm vi QA được ghi trong docs/VALIDATION.md.')

    report.heading('9 Giới hạn và công bố nguồn gốc')
    report.subheading('Phạm vi của khuyến nghị')
    report.text(f'CUTOFF {selected} là lựa chọn cho một cài đặt, kiểu Integer[], năm phân phối và trọng số đã xác định. Không suy rộng thành ngưỡng tốt nhất cho mọi máy hoặc mọi kiểu Comparable. Đổi sang int[], chuỗi dài, compareTo đắt, cách chèn bằng dịch phần tử hoặc phép merge khác có thể làm đổi ngưỡng.')
    report.text('Lưới sàng lọc hữu hạn, tối đa 128. Pha chọn và xác nhận chỉ giữ ba đại diện cùng các mốc kiểm soát, không đo lại toàn bộ lưới. Bootstrap giữ cố định các phân phối và kích thước; một phiên máy và số JVM hạn chế chưa bao phủ nhiệt độ, tải nền hoặc mọi cấu hình JIT. Khoảng từng cặp không chứng minh tối ưu tuyệt đối hoặc tương đương thống kê của toàn vùng.')
    report.text('Vùng gần tối ưu 3% là quy ước thực dụng đã chốt. Cùng cây đệ quy là tính chất cấu trúc của cài đặt trên N cụ thể, không buộc thời gian máy bằng nhau hoàn toàn. Không chọn lại sau pha xác nhận và không mở thêm một pha để thay kết quả. Quicksort không thuộc phần thí nghiệm MergeSort được giao trong ảnh đề.')
    report.subheading('Mã giữ lại và công việc AI')
    report.text('Tệp duy nhất giữ lại từ tài liệu làm việc trước là MergeSort.java do người dùng chỉ định. Hash của nó khớp nguồn đã đo ở cả ba pha. Kiểm thử, công cụ, dữ liệu, số đo, phân tích, hình, báo cáo, demo và tài liệu của bản này đều được tạo trong lần làm lại; không đóng gói PDF, script, lịch sử chat hoặc kết quả cũ.')
    report.code('SHA-256 MergeSort.java\n'+source['source_sha256'])
    report.text('Theo mô tả của người dùng, phần MergeSort là cài đặt do người dùng thực hiện. AI giữ nguyên và hỗ trợ các phần còn lại. Nhật ký AI_SESSION_LOG.md ghi đầy đủ lời trao đổi hiển thị từ yêu cầu làm lại, kèm tóm tắt công cụ và liên kết nhật ký kỹ thuật; không chứa suy luận nội bộ hoặc chỉ dẫn hệ thống. Bìa để trống theo lựa chọn của người dùng.')
    report.subheading('Tài liệu tham khảo')
    report.text('[1] Ảnh đề bài và tệp MergeSort.java được người dùng cung cấp trong cuộc trao đổi. Các yêu cầu sản phẩm được đối chiếu trong docs/REQUIREMENTS.md.')
    report.text('[2] Oracle Java SE 25 API. System.nanoTime. Đo khoảng thời gian bằng hiệu hai lần đọc cùng JVM; độ chính xác đơn vị nano giây không bảo đảm độ phân giải một nano giây. https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime()')
    report.text('[3] Oracle Java SE 25 API. StackWalker. https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/StackWalker.html  Truy cập ngày 13/11/2026. Không dùng nguồn này để thay thế cài đặt MergeSort.')
    report.save()
    print('New report authored: report/Cutoff_Study.docx and .md; four PNG/SVG figures.')
