from django.http import HttpResponse
from django.utils import timezone
import xlsxwriter
from io import BytesIO

class ExcelExportMixin:
   
    
    def get_export_queryset(self, request):
        
        return self.get_queryset(request)
    
    def get_export_fields(self):
        
        return self.list_display
    
    def dehydrate_field(self, obj, field_name):
        
        if hasattr(self, f'dehydrate_{field_name}'):
            return getattr(self, f'dehydrate_{field_name}')(obj)
        return getattr(obj, field_name)
    
    def get_field_header(self, field_name):
        
        if hasattr(self, f'get_{field_name}_header'):
            return getattr(self, f'get_{field_name}_header')()
        return field_name.replace('_', ' ').title()
    
    def export_as_excel(self, request, queryset):
        
        # Create a BytesIO object to store the Excel file
        output = BytesIO()
        
        # Create a new Excel workbook and worksheet
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # Get fields to export
        fields = self.get_export_fields()
        
        # Write headers
        for col, field in enumerate(fields):
            header = self.get_field_header(field)
            worksheet.write(0, col, header)
        
        # Write data
        for row, obj in enumerate(queryset, start=1):
            for col, field in enumerate(fields):
                value = self.dehydrate_field(obj, field)
                worksheet.write(row, col, str(value))
        
        # Close the workbook
        workbook.close()
        
        # Set up the response
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return response
    
    export_as_excel.short_description = "Генерация execle" 