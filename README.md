# Mini-Project
For Datawarehouse
### สมาชิก
1.นางสาวกนกวรรณ ทองเทพ รหัสนักศึกษา 673020243-5
   
2.นายณัฐวุฒิ กำจัดภัย รหัสนักศึกษา 673020251-6
   
3.นางสาวณิรดา อนุนิวัฒน์ รหัสนักศึกษา 673020252-4
   
4.นายภูธิป ต้นโลห์ รหัสนักศึกษา 673020261-3

5.นางสาวสุพิชชา คำสิงห์ รหัสนักศึกษา 673020265-5

6.นายสุวิชชา ผาสุข รหัสนักศึกษา 673020267-1

7.นายอพิชัย อิ่มวงค์ รหัสนักศึกษา 673020269-7

## การออกแบบและพัฒนาคลังข้อมูลเพื่อวิเคราะห์ข้อมูลการขายในธุรกิจค้าปลีก (Retail Analytics: From OLTP to OLAP Data Warehouse)

   มีวัตถุประสงค์เพื่อออกแบบและพัฒนาระบบคลังข้อมูลสำหรับธุรกิจค้าปลีก โดยนำข้อมูลจากฐานข้อมูลปฏิบัติการ (OLTP) มาผ่านกระบวนการ ETL/ELT เพื่อทำความสะอาดและแปลงข้อมูล จากนั้นจัดเก็บข้อมูลใน Data Warehouse ที่ออกแบบด้วยแนวคิด Dimensional Modeling และ Star Schema ประกอบด้วย Fact Table และ Dimension Tables เพื่อรองรับการวิเคราะห์ข้อมูลในมิติต่าง ๆ เช่น เวลา สินค้า ลูกค้า และสาขา ระบบจะนำข้อมูลจาก Data Warehouse มาวิเคราะห์ด้วยแนวคิด OLAP และพัฒนา Interactive Dashboard เพื่อแสดงยอดขาย จำนวนคำสั่งซื้อ กำไร สินค้าขายดี และตัวชี้วัดทางธุรกิจอื่น ๆ สำหรับสนับสนุนการตัดสินใจทางธุรกิจ

### Dataset & Operational Database
ความหมายของ Dataset

1. Dataset คือชุดข้อมูลที่นำมาใช้ในการทำโครงงาน โดย Dataset นี้เป็นข้อมูลเกี่ยวกับ การขายสินค้าและการดำเนินงานของร้านค้าปลีก (Retail) ซึ่งประกอบด้วยข้อมูลลูกค้า สินค้า ร้านค้า คำสั่งซื้อ การชำระเงิน การจัดส่ง และการคืนสินค้า

2. Dataset นี้เป็นข้อมูลของ ระบบการขายสินค้าของธุรกิจค้าปลีก โดยจำลองกระบวนการตั้งแต่ลูกค้าเข้ามาสั่งซื้อสินค้า จนถึงการชำระเงิน การจัดส่ง และการคืนสินค้า
ตารางหลักของ Dataset
## รายละเอียดตารางข้อมูล

| ลำดับ | ตาราง | จำนวน Records | จำนวน Columns | รายละเอียด |
|:---:|---|---:|---:|---|
| 1 | `employees` | 1,000 | 3 | ข้อมูลพนักงาน |
| 2 | `returns` | 30,000 | 3 | ข้อมูลการคืนสินค้า |
| 3 | `products` | 10,000 | 4 | ข้อมูลสินค้า |
| 4 | `suppliers` | 200 | 2 | ข้อมูลผู้จัดจำหน่าย |
| 5 | `categories` | 30 | 2 | ข้อมูลประเภทสินค้า |
| 6 | `promotions` | 50 | 2 | ข้อมูลโปรโมชั่น |
| 7 | `stores` | 100 | 2 | ข้อมูลสาขา |
| 8 | `customers` | 50,000 | 3 | ข้อมูลลูกค้า |
| 9 | `payments` | 300,000 | 3 | ข้อมูลการชำระเงิน |
| 10 | `orders` | 300,000 | 5 | ข้อมูลคำสั่งซื้อ |
| 11 | `order_items` | 600,000 | 5 | รายละเอียดสินค้าในคำสั่งซื้อ |
| 12 | `shipments` | 300,000 | 3 | ข้อมูลการจัดส่ง |
Dataset หลักทั้ง 12 ตารางมีข้อมูลรวมทั้งหมด 1,591,380 Records และ 39 Columns

https://colab.research.google.com/drive/1cb03m3na2yEKvnH9-JK1oxXGFHjB0PGo#scrollTo=b8417809

3. OLTP (Online Transaction Processing)

OLTP (Online Transaction Processing) หรือ ระบบประมวลผลรายการธุรกรรมออนไลน์ เป็นระบบฐานข้อมูลที่ใช้สำหรับจัดเก็บและประมวลผลธุรกรรมที่เกิดขึ้นจากการดำเนินงานประจำวันขององค์กร โดยมีจุดมุ่งหมายเพื่อให้สามารถบันทึก แก้ไข และเรียกใช้ข้อมูลธุรกรรมได้อย่างรวดเร็ว ถูกต้อง และเป็นระบบ รวมถึงสามารถรองรับธุรกรรมจำนวนมากและการทำงานของผู้ใช้งานหลายคนพร้อมกัน

สำหรับ Dataset ที่นำมาใช้ในโครงงานนี้ มีลักษณะเป็นข้อมูลของ ระบบธุรกิจค้าปลีก (Retail Business) ซึ่งประกอบด้วยข้อมูลลูกค้า สินค้า ร้านค้า พนักงาน ผู้จัดจำหน่าย ประเภทสินค้า โปรโมชั่น ตลอดจนข้อมูลการสั่งซื้อ การชำระเงิน การจัดส่ง และการคืนสินค้า โดย Dataset หลักประกอบด้วย 12 ตาราง จำนวนรวม 1,591,380 Records และ 39 Columns

จากการศึกษาลักษณะและโครงสร้างของข้อมูล พบว่า Dataset มีความสอดคล้องกับระบบ OLTP เนื่องจากมีทั้ง ข้อมูลหลัก (Master Data) และ ข้อมูลธุรกรรม (Transaction Data) ซึ่งทำงานเชื่อมโยงกันเพื่อรองรับกระบวนการขายสินค้า

3.1 ข้อมูลหลัก (Master Data)

ข้อมูลหลักเป็นข้อมูลที่ใช้ประกอบการทำธุรกรรมและไม่ได้เกิดขึ้นใหม่ทุกครั้งที่มีการซื้อสินค้า ประกอบด้วยตารางต่าง ๆ ดังนี้

## รายละเอียดตารางข้อมูลหลัก

| ตาราง | รายละเอียด | ตัวอย่างข้อมูล | จำนวน Records |
|:---:|:---|:---|---:|
| `customers` | ใช้จัดเก็บข้อมูลลูกค้า | `customer_id`, `city`, `signup_date` | 50,000 |
| `products` | ใช้จัดเก็บข้อมูลสินค้า | `product_id`, `category_id`, `supplier_id`, `price` | 10,000 |
| `categories` | ใช้จัดเก็บข้อมูลประเภทสินค้า | `category_id`, `category_name` | 30 |
| `suppliers` | ใช้จัดเก็บข้อมูลผู้จัดจำหน่าย | `supplier_id`, `supplier_name` | 200 |
| `stores` | ใช้จัดเก็บข้อมูลสาขา | `store_id`, `store_name` | 100 |
| `employees` | ใช้จัดเก็บข้อมูลพนักงาน | `employee_id`, `employee_name`, `store_id` | 1,000 |
| `promotions` | ใช้จัดเก็บข้อมูลโปรโมชั่น | `promotion_id`, `promotion_name` | 50 |

ข้อมูลเหล่านี้จะถูกนำมาใช้ประกอบการทำธุรกรรม เช่น เมื่อมีการสั่งซื้อสินค้า ระบบจะนำข้อมูลลูกค้า สินค้า สาขา และโปรโมชั่นที่เกี่ยวข้องมาเชื่อมโยงกับคำสั่งซื้อ

3.2 ข้อมูลธุรกรรม (Transaction Data)

ข้อมูลธุรกรรมเป็นข้อมูลที่เกิดขึ้นจากกิจกรรมต่าง ๆ ของระบบ โดยมีการเพิ่มข้อมูลเมื่อเกิดเหตุการณ์ใหม่ เช่น การสั่งซื้อ การชำระเงิน หรือการจัดส่ง ประกอบด้วย

## รายละเอียดตารางข้อมูล

| ตาราง | รายละเอียด | ตัวอย่างข้อมูล | จำนวน Records |
|:---:|:---|:---|---:|
| `customers` | ใช้จัดเก็บข้อมูลลูกค้า | `customer_id`, `city`, `signup_date` | 50,000 |
| `products` | ใช้จัดเก็บข้อมูลสินค้า | `product_id`, `category_id`, `supplier_id`, `price` | 10,000 |
| `categories` | ใช้จัดเก็บข้อมูลประเภทสินค้า | `category_id`, `category_name` | 30 |
| `suppliers` | ใช้จัดเก็บข้อมูลผู้จัดจำหน่าย | `supplier_id`, `supplier_name` | 200 |
| `stores` | ใช้จัดเก็บข้อมูลสาขา | `store_id`, `store_name` | 100 |
| `employees` | ใช้จัดเก็บข้อมูลพนักงาน | `employee_id`, `employee_name`, `store_id` | 1,000 |
| `promotions` | ใช้จัดเก็บข้อมูลโปรโมชั่น | `promotion_id`, `promotion_name` | 50 |
| `orders` | ใช้บันทึกข้อมูลคำสั่งซื้อ | `order_id`, `customer_id`, `store_id`, `order_date`, `promotion_id` | 300,000 |
| `order_items` | ใช้บันทึกรายละเอียดสินค้าในแต่ละคำสั่งซื้อ | `order_item_id`, `order_id`, `product_id`, `qty`, `price` | 600,000 |
| `payments` | ใช้บันทึกข้อมูลการชำระเงิน | `payment_id`, `order_id`, `amount` | 300,000 |
| `shipments` | ใช้บันทึกข้อมูลการจัดส่ง | `shipment_id`, `order_id`, `status` | 300,000 |
| `returns` | ใช้บันทึกข้อมูลการคืนสินค้า | `return_id`, `order_item_id`, `refund` | 30,000 |
ตารางเหล่านี้มีความสำคัญต่อระบบ OLTP เนื่องจากเป็นข้อมูลที่เกิดขึ้นจากธุรกรรมโดยตรงและมีการบันทึกข้อมูลเป็นรายรายการ

3.3 กระบวนการทำงานของ OLTP ใน Dataset

การทำงานของระบบสามารถอธิบายเป็นกระบวนการตั้งแต่ลูกค้าทำการสั่งซื้อจนถึงการจัดส่งสินค้าได้ดังนี้

ขั้นตอนที่ 1 ลูกค้า

ลูกค้าถูกจัดเก็บในตาราง customers โดยมี customer_id เป็นรหัสสำหรับระบุลูกค้าแต่ละราย

↓

ขั้นตอนที่ 2 การสั่งซื้อสินค้า

เมื่อลูกค้าทำการสั่งซื้อ ระบบจะสร้างข้อมูลในตาราง orders โดยกำหนด order_id เพื่อระบุคำสั่งซื้อแต่ละรายการ และเชื่อมโยงกับ customer_id เพื่อระบุว่าคำสั่งซื้อเป็นของลูกค้ารายใด

↓

ขั้นตอนที่ 3 การบันทึกรายการสินค้า

รายละเอียดสินค้าที่อยู่ภายในคำสั่งซื้อจะถูกบันทึกใน order_items โดยใช้ order_id เชื่อมโยงกับคำสั่งซื้อ และใช้ product_id เชื่อมโยงกับข้อมูลสินค้าใน products

↓

ขั้นตอนที่ 4 การชำระเงิน

เมื่อมีการชำระเงิน ระบบจะบันทึกข้อมูลลงใน payments โดยใช้ order_id เพื่อระบุว่าการชำระเงินนั้นเกี่ยวข้องกับคำสั่งซื้อใด

↓

ขั้นตอนที่ 5 การจัดส่ง

เมื่อดำเนินการจัดส่ง ระบบจะสร้างข้อมูลใน shipments และใช้ status เพื่อระบุสถานะของการจัดส่ง

↓

ขั้นตอนที่ 6 การคืนสินค้า

หากลูกค้าต้องการคืนสินค้า ระบบจะบันทึกข้อมูลใน returns และใช้ order_item_id เพื่อระบุว่าสินค้าที่คืนเป็นรายการใดในคำสั่งซื้อ
ดังนั้น กระบวนการโดยรวมสามารถแสดงได้ดังนี้

Customer → Order → Order Item → Payment → Shipment → Return

3.4 ความสัมพันธ์ของข้อมูลที่สนับสนุนการทำงานแบบ OLTP

อีกหนึ่งลักษณะสำคัญของ Dataset คือการมีการเชื่อมโยงข้อมูลระหว่างตารางผ่านรหัสประจำข้อมูล เช่น

customer_id เชื่อมโยงข้อมูลลูกค้ากับคำสั่งซื้อ
order_id เชื่อมโยงคำสั่งซื้อกับรายละเอียดสินค้า การชำระเงิน และการจัดส่ง
product_id เชื่อมโยงรายการสินค้าเข้ากับข้อมูลสินค้า
category_id เชื่อมโยงสินค้าเข้ากับประเภทสินค้า
supplier_id เชื่อมโยงสินค้าเข้ากับผู้จัดจำหน่าย
store_id เชื่อมโยงคำสั่งซื้อและพนักงานกับสาขา
promotion_id เชื่อมโยงคำสั่งซื้อกับโปรโมชั่น
order_item_id เชื่อมโยงรายการสินค้าเข้ากับข้อมูลการคืนสินค้า

การแบ่งข้อมูลออกเป็นหลายตารางและเชื่อมโยงกันดังกล่าวช่วยลดการจัดเก็บข้อมูลซ้ำซ้อน และทำให้สามารถจัดการข้อมูลแต่ละส่วนได้อย่างเป็นระบบ

3.5 เหตุผลที่ Dataset มีลักษณะเป็น OLTP

จากการตรวจสอบ Dataset สามารถระบุเหตุผลที่สนับสนุนว่า Dataset นี้มีลักษณะเป็น OLTP ได้ดังนี้

ประการที่หนึ่ง Dataset มีตารางที่ใช้บันทึกธุรกรรมโดยตรง เช่น orders, order_items, payments, shipments และ returns

ประการที่สอง มีตารางข้อมูลหลัก เช่น customers, products, stores, categories, suppliers, employees และ promotions ซึ่งทำหน้าที่สนับสนุนการทำธุรกรรม

ประการที่สาม ข้อมูลมีรายละเอียดในระดับรายการธุรกรรม เช่น order_items สามารถระบุได้ว่าคำสั่งซื้อหนึ่งรายการประกอบด้วยสินค้าอะไร จำนวนเท่าใด และราคาเท่าใด

ประการที่สี่ Dataset มีจำนวนข้อมูลค่อนข้างมาก โดยมีข้อมูลรวม 1,631,380 Records ซึ่งส่วนใหญ่เป็นข้อมูลธุรกรรม เช่น order_items จำนวน 600,000 Records และ orders, payments และ shipments ตารางละ 300,000 Records

ประการที่ห้า ตารางต่าง ๆ มีการเชื่อมโยงข้อมูลด้วยรหัส เช่น order_id, customer_id และ product_id ซึ่งเป็นลักษณะสำคัญของฐานข้อมูลที่ใช้จัดการธุรกรรม

ประการที่หก โครงสร้างของ Dataset สามารถสะท้อนกระบวนการดำเนินงานของธุรกิจค้าปลีกตั้งแต่การสั่งซื้อ การบันทึกรายการสินค้า การชำระเงิน การจัดส่ง และการคืนสินค้า

3.6 สรุปการวิเคราะห์ OLTP

จากการวิเคราะห์ Dataset พบว่า Dataset มีลักษณะสอดคล้องกับ OLTP (Online Transaction Processing) เนื่องจากเป็นข้อมูลที่ใช้สนับสนุนกระบวนการดำเนินงานของธุรกิจค้าปลีก โดยมีทั้งข้อมูลหลักและข้อมูลธุรกรรมที่มีการเชื่อมโยงกันอย่างเป็นระบบ

ข้อมูลธุรกรรมที่สำคัญ ได้แก่ orders, order_items, payments, shipments และ returns ซึ่งทำหน้าที่บันทึกเหตุการณ์ต่าง ๆ ที่เกิดขึ้นจากการดำเนินงาน ขณะที่ customers, products, categories, suppliers, stores, employees และ promotions ทำหน้าที่เป็นข้อมูลหลักที่ใช้ประกอบการทำธุรกรรม

นอกจากนี้ Dataset ยังมีการเชื่อมโยงข้อมูลผ่านรหัสต่าง ๆ เช่น customer_id, order_id, product_id และ store_id ทำให้สามารถติดตามข้อมูลของธุรกรรมตั้งแต่การสั่งซื้อจนถึงการชำระเงิน การจัดส่ง และการคืนสินค้าได้

ดังนั้น Dataset นี้สามารถจัดอยู่ในลักษณะของฐานข้อมูล OLTP สำหรับระบบค้าปลีก เนื่องจากมีโครงสร้างที่มุ่งเน้นการจัดเก็บข้อมูลธุรกรรมที่เกิดขึ้นในแต่ละวัน มีข้อมูลในระดับรายละเอียดของ Transaction และมีความสัมพันธ์ระหว่างข้อมูลหลายตารางเพื่อสนับสนุนกระบวนการทำงานของระบบค้าปลีกอย่างเป็นระบบและมีประสิทธิภาพ



## ER Diagram (หลิน)
<img src="./readme_images/Miniproject Diagram.drawio (1).png">
## Database Relationships

| Table | Relationship | Table |
|---|:---:|---|
| categories | 1:N | products |
| suppliers | 1:N | products |
| products | 1:N | order_items |
| orders | 1:N | order_items |
| order_items | 1:N | returns |
| customers | 1:N | orders |
| stores | 1:N | orders |
| promotions | 1:N | orders |
| orders | 1:N | payments |
| orders | 1:N | shipments |
| stores | 1:N | employees |

## Business Questions (ฟีฟ่า)

<img width="2481" height="3509" alt="Business Questions + KPI + แนวทางการวิเคราะห์_pages-to-jpg-0001" src="https://github.com/user-attachments/assets/9e722ba4-a7f5-4f9a-b15c-2656578d17d0" />
<img width="2481" height="3509" alt="Business Questions + KPI + แนวทางการวิเคราะห์_pages-to-jpg-0002" src="https://github.com/user-attachments/assets/82c15f58-89e1-46f5-8bcd-47866d7e536e" />
<img width="2481" height="3509" alt="Business Questions + KPI + แนวทางการวิเคราะห์_pages-to-jpg-0003" src="https://github.com/user-attachments/assets/0afbc732-5f5c-4ae6-8092-93bda6e92caf" />


## Multidimensional Data Model Design (ต้นข้าว)
เริ่มจากการวิเคราะห์ข้อมูลจากระบบขายปลีกที่ประกอบด้วยไฟล์ข้อมูล 12 ตาราง ได้แก่ Categories, Customers, Employees, Order Items, Orders, Payments, Products, Promotions, Returns, Shipments, Stores และ Suppliers
จากนั้นกำหนด Business Process หลัก คือ กระบวนการขายสินค้า (Sales Process) เนื่องจากเป็นกระบวนการที่เชื่อมโยงข้อมูลส่วนใหญ่ของระบบ เช่น ลูกค้า สินค้า ร้านค้า พนักงาน โปรโมชั่น การชำระเงิน และการจัดส่งสินค้า
จากนั้นแยกข้อมูลเชิงพรรณนาออกเป็น Dimension Tables และเก็บข้อมูลเชิงตัวเลขที่ใช้วิเคราะห์ไว้ใน Fact Table
- Dim_Date: Day → Month → Quarter → Year
ใช้ในการดูยอดขายแต่ละวัน เดือน ไตรมาส และปี
- Dim_Product: Category → Sub-Category
ใช้ในการจัดหมวดหมู่ผลิตภัณฑ์
- Dim_Customer: Customer
ใช้ในการวิเคราะห์พฤติกรรมของลูกค้า
- Dim_Store: Store → District → Province → Region
ใช้ในการวิเคราะห์ผลการดำเนินงานรายสาขาและพื้นที่
- Dim_Employee: Employee
ใช้ในการวิเคราะห์พฤติกรรมการทำงานของพนักงาน
- Dim_Promotion: Promotion => Discount, Special Deal, Cupon, Point
ใช้ในการวิเคราะห์ส่วนของโปรโมชั่น เช่น ส่วนลด ของแถม ดีล คูปอง และ พอยท์
- Dim_Supplier: Supplier
ใช้ในการวิเคราะห์เรื่องซัพพลายเออร์,การจัดการทรัพยากร
- Dim_Payment: Payment Method ใช้ในการวิเคราห์วิธีการชำระเงินของลูกค้า

ในส่วนของ Fact Tables [Fact_Sales] จะมี Source หลักๆ คือ
- Order_items.csv
- Orders.csv

ในส่วนไฟล์ข้อมูล Returns และ Shipments สามารถนำมาสร้างเป็น Fact แยกออกมา
- Returns  → Fact_Returns เพื่อวิเคราะห์อัตราการคืนสินค้า (Return Rate) ตามสาขา หรือตามประเภทสินค้า
- Shipments  →  Fact_Shipments เพื่อวัดประสิทธิภาพระยะเวลาจัดส่ง (Delivery Lead Time) และคลังสินค้า

กำหนด Grain ของ Fact Table ว่า
	“1 แถว แทนสินค้า 1 รายการในคำสั่งซื้อ 1 รายการ (One Order Line Item)”

Foreign Keys:
- Date_ID
- Product_ID
- Customer_ID
- Store_ID
- Employee_ID
- Promotion_ID
- Supplier_ID
- Payment_ID

Measure
- Quantity (จำนวนสินค้า) จำนวนชิ้นที่ขายได้ในรายการนั้น
- Sales Amount (ยอดขาย) จำนวนเงินรวมหลังหักส่วนลด หรือราคาสุทธิ
- Discount (ส่วนลด) มูลค่าส่วนลดที่ให้ในรายการนั้น
- Profit (กำไรสุทธิ) กำไรสุทธิจากรายการนั้น
- Calculated MeasuresProfit Margin (%):
  - ("Profit" /"Sales Amount" )×100
  - Average Selling Price (ราคาขายเฉลี่ยต่อชิ้น): "Sales Amount"/"Quantity" 

## Data Model Diagram (Star Scheme) แซนด์วิช
<img src="./readme_images/star schema.jpg">

## การดำเนินงานด้านการจัดการข้อมูลด้วยกระบวนการ ELT

## 1. กระบวนการ ELT (ELT Process)

1.1 หลักการและแนวคิดของ ELT

โครงงานนี้ใช้กระบวนการ ELT (Extract, Load, Transform) ในการจัดการข้อมูล โดยมีวัตถุประสงค์เพื่อรวบรวมข้อมูลจากระบบต้นทาง จัดเก็บข้อมูลในฐานข้อมูล และดำเนินการทำความสะอาดและแปลงข้อมูลภายหลังจากที่ข้อมูลถูก Load เข้าสู่ฐานข้อมูลแล้ว

ELT ประกอบด้วย 3 ขั้นตอนหลัก ได้แก่

Extract – การดึงข้อมูลจากแหล่งข้อมูลต้นทาง
Load – การนำข้อมูลเข้าสู่ฐานข้อมูลในรูปแบบ Raw/Staging
Transform – การทำความสะอาด แปลง และจัดโครงสร้างข้อมูลเพื่อเตรียมเข้าสู่ Data Warehouse

| ขั้นตอน (Stage) | ชื่อชั้นข้อมูล (Layer Name) | เครื่องมือ / เทคโนโลยี (Tools) | หน้าที่และการทำงาน (Function / Tasks) |
| :--- | :--- | :--- | :--- |
| **1. Source** | **แหล่งข้อมูลต้นทาง** | Google Drive / CSV Files | จัดเก็บไฟล์ข้อมูลดิบรูปแบบ CSV บน Google Drive พร้อมสำหรับการดึงไปใช้งาน |
| **2. Extract** | **Raw / Staging** | DuckDB | ทำการดึงข้อมูลดิบ (Extract) เข้าสู่พื้นที่พักข้อมูล (Staging Area) เพื่อเตรียมนำไปแปลงสภาพ |
| **3. Transform** | **Transform Layer** | Data Processing Engine | ทำการทำความสะอาดข้อมูล (Cleaning), เชื่อมโยงข้อมูล (Join), แปลงชนิดข้อมูล (Type Conversion) และคำนวณค่าต่างๆ (Calculation) |
| **4. Storage** | **Data Warehouse** | Relational / Analytical DB | จัดเก็บข้อมูลที่ผ่านการแปลงแล้วลงในรูปแบบ **Fact Tables** (ตารางข้อเท็จจริง) และ **Dimension Tables** (ตารางมิติ) |
| **5. Output** | **Analysis** | BI Tools / Dashboards / SQL | นำข้อมูลที่จัดเก็บใน Data Warehouse ไปวิเคราะห์ ทำรายงาน หรือนำเสนอต่อผู้ใช้งาน |

## 1.2 โครงสร้าง Dataset

Dataset ที่ใช้ในโครงงานเป็นข้อมูลระบบค้าปลีก ประกอบด้วยข้อมูลเกี่ยวกับลูกค้า สินค้า ร้านค้า คำสั่งซื้อ การชำระเงิน การจัดส่ง การคืนสินค้า โปรโมชั่น และข้อมูลที่เกี่ยวข้องกับการดำเนินงานของธุรกิจค้าปลีก

จากการตรวจสอบข้อมูลพบ 12 ตารางหลัก ดังนี้
นอกจากนี้ยังพบไฟล์ข้อมูลประเภท TXT และ ZIP ซึ่งเป็นข้อมูลตัวอย่างขนาดเล็ก จึงแยกออกจาก Dataset หลักเพื่อให้การวิเคราะห์โครงสร้างฐานข้อมูลค้าปลีกมีความชัดเจน

| ลำดับ | ตาราง | Records | Columns | ประเภทข้อมูล |
| :---: | :--- | :---: | :---: | :---: |
| 1 | employees | 1,000 | 3 | Master |
| 2 | returns | 30,000 | 3 | Transaction |
| 3 | products | 10,000 | 4 | Master |
| 4 | suppliers | 200 | 2 | Master |
| 5 | categories | 30 | 2 | Master |
| 6 | promotions | 50 | 2 | Master |
| 7 | stores | 100 | 2 | Master |
| 8 | customers | 50,000 | 3 | Master |
| 9 | payments | 300,000 | 3 | Transaction |
| 10 | orders | 300,000 | 5 | Transaction |
| 11 | order_items | 600,000 | 5 | Transaction |
| 12 | shipments | 300,000 | 3 | Transaction |

รวมข้อมูลทั้งหมด
<1,631,380 Records และ 39 Columns>


# ๒Retail Data Warehouse — End-to-End ELT Pipeline with DuckDB

> **Project Documentation | Extract → Load → Transform Architecture**  
> *เอกสารสรุปการพัฒนาระบบ คลังข้อมูลสินค้าปลีก ด้วย Python, Pandas และ DuckDB*

การดำเนินงานใช้ **Google Colab** ร่วมกับ **DuckDB** และ **Pandas**

```python
# 1.3.1 ติดตั้ง Library และ Import
!pip install duckdb -q

import pandas as pd
import duckdb
import os
from google.colab import drive

# 1.3.2 เชื่อมต่อ Google Drive
drive.mount('/content/drive')

# 1.3.3 กำหนด Path ของ Dataset
path = '/content/drive/My Drive/miniproject_สินค้าปลีก'
print("Dataset Path:", path)
print("Files:", os.listdir(path))
1.4 Extract Phaseกระบวนการดึงข้อมูลจากไฟล์ CSV ทั้ง 12 ตารางเข้ามาประมวลผลบน PythonPython# 1.4.2 กำหนดรายชื่อตาราง
tables = [
    'employees', 'returns', 'products', 'suppliers',
    'categories', 'promotions', 'stores', 'customers',
    'payments', 'orders', 'order_items', 'shipments'
]

# 1.4.3 อ่านข้อมูล CSV เข้า Pandas DataFrame
loaded_data = {}
for table in tables:
    file_path = os.path.join(path, table + '.csv')
    df = pd.read_csv(file_path)
    loaded_data[table] = df
    print(f"{table}.csv -> {len(df):,} records")
1.5 Load Phase (Staging Layer)นำข้อมูลจาก Pandas/CSV เข้าสู่ DuckDB โดยสร้างเป็น Staging Tables (stg_*) เพื่อทำ Persistence ข้อมูลก่อน TransformPython# 1.5.2 สร้างการเชื่อมต่อ DuckDB
db_path = os.path.join(path, 'retail.duckdb')
con = duckdb.connect(db_path)

# 1.5.3 Load CSV -> Staging Tables
for table in tables:
    file_path = os.path.join(path, table + '.csv')
    con.execute(f"""
        CREATE OR REPLACE TABLE stg_{table} AS
        SELECT * FROM read_csv_auto(?)
    """, [file_path])
    print(f"Loaded: {table}.csv -> stg_{table}")
ข้อดีของการใช้ Staging LayerData Persistence: เก็บข้อมูลจาก Source ไว้ใน Database โดยตรงPerformance: ลดการอ่านไฟล์ CSV ซ้ำหลายครั้งValidation: ตรวจสอบความถูกต้อง (Missing Values, Duplicates, Data Type) ก่อนนำไป TransformArchitecture Separation: แยก Source Data ออกจาก Transformation Logic อย่างชัดเจน1.6 Transform Phase & Data Cleaningทำการตรวจสอบคุณภาพข้อมูล และปรับแต่งให้พร้อมใช้งานสำหรับ Data Warehouse1.6.1 Data Quality Check ScriptsPython# ตรวจสอบ Missing Values และ Duplicates
for table in tables:
    df = con.execute(f"SELECT * FROM stg_{table}").df()
    print("=" * 50)
    print(f"Table: {table}")
    print("Missing Values:\n", df.isnull().sum())
    print("Duplicate Records:", df.duplicated().sum())
1.6.2 Data Cleaning & Transformation Rulesกฎการจัดการ (Rule)รายละเอียดการทำงานMissing Valueตรวจสอบค่าว่างทุกคอลัมน์ (พบ 0 Missing Values)Duplicatesตรวจสอบและกำจัดแถวที่ซ้ำซ้อน (พบ 0 Duplicate Rows)Primary Key Validationตรวจสอบความซ้ำซ้อนของ PK (COUNT > 1 = 0)Foreign Key Validationตรวจสอบ Referential Integrity ระหว่างตารางDate Conversionแปลง Text/String Date เป็น DATE Type ผ่าน TRY_CAST()Measure Calculationคำนวณยอดขาย sales_amount = qty * price ใน fact_order_itemsSurrogate Keysสร้าง Primary Key ใหม่สำหรับ Dimension ด้วย ROW_NUMBER()1.7 Dimension Tables Modelingสร้าง Dimension Tables ทั้ง 7 ตารางเพื่อเก็บ Attribute รายละเอียดของธุรกิจ:SQL-- 1.7.1 Dim Customer
CREATE OR REPLACE TABLE dim_customer AS
SELECT ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_sk, customer_id, city, TRY_CAST(signup_date AS DATE) AS signup_date
FROM stg_customers;

-- 1.7.2 Dim Product
CREATE OR REPLACE TABLE dim_product AS
SELECT ROW_NUMBER() OVER (ORDER BY product_id) AS product_sk, product_id, category_id, supplier_id, price
FROM stg_products;

-- 1.7.3 Dim Store
CREATE OR REPLACE TABLE dim_store AS
SELECT ROW_NUMBER() OVER (ORDER BY store_id) AS store_sk, store_id, city
FROM stg_stores;

-- 1.7.4 Dim Category
CREATE OR REPLACE TABLE dim_category AS
SELECT ROW_NUMBER() OVER (ORDER BY category_id) AS category_sk, category_id, category_name
FROM stg_categories;

-- 1.7.5 Dim Supplier
CREATE OR REPLACE TABLE dim_supplier AS
SELECT ROW_NUMBER() OVER (ORDER BY supplier_id) AS supplier_sk, supplier_id, country
FROM stg_suppliers;

-- 1.7.6 Dim Promotion
CREATE OR REPLACE TABLE dim_promotion AS
SELECT ROW_NUMBER() OVER (ORDER BY promotion_id) AS promotion_sk, promotion_id, discount
FROM stg_promotions;

-- 1.7.7 Dim Employee
CREATE OR REPLACE TABLE dim_employee AS
SELECT ROW_NUMBER() OVER (ORDER BY employee_id) AS employee_sk, employee_id, store_id, salary
FROM stg_employees;
1.8 Fact Tables Modelingสร้าง Fact Tables ทั้ง 5 ตารางเพื่อเก็บรายการธุรกรรมและค่าตัวเลขเชิงปริมาณ (Measures):SQL-- 1.8.1 Fact Orders
CREATE OR REPLACE TABLE fact_orders AS
SELECT order_id, customer_id, store_id, TRY_CAST(order_date AS DATE) AS order_date, promotion_id
FROM stg_orders;

-- 1.8.2 Fact Order Items (Calculated Measure: sales_amount)
CREATE OR REPLACE TABLE fact_order_items AS
SELECT order_item_id, order_id, product_id, qty, price, qty * price AS sales_amount
FROM stg_order_items;

-- 1.8.3 Fact Payments
CREATE OR REPLACE TABLE fact_payments AS
SELECT payment_id, order_id, amount
FROM stg_payments;

-- 1.8.4 Fact Shipments
CREATE OR REPLACE TABLE fact_shipments AS
SELECT shipment_id, order_id, status
FROM stg_shipments;

-- 1.8.5 Fact Returns
CREATE OR REPLACE TABLE fact_returns AS
SELECT return_id, order_item_id, refund
FROM stg_returns;

1.9 Data Warehouse Relationship Map (Star Schema)แผนผังแสดงความสัมพันธ์ระหว่าง Dimension Tables และ Fact Tables:                  ┌─────────────────┐
                  │  dim_customer   │
                  └────────┬────────┘
                           │ customer_id
                           ▼
                  ┌─────────────────┐
                  │   fact_orders   │ ◄─── store_id ────── ┌───────────────┐
                  └────────┬────────┘                      │   dim_store   │
                           │                               └───────────────┘
                           │ order_id
                           ▼
                  ┌─────────────────┐
                  │fact_order_items │ ◄─── product_id ──── ┌───────────────┐
                  └────────┬────────┘                      │  dim_product  │
                           │                               └───────┬───────┘
                           │ order_item_id                         │
                           ▼                                       ├─► dim_category
                  ┌─────────────────┐                              │
                  │  fact_returns   │                              └─► dim_supplier
                  └─────────────────┘

Markdown## 1.10 ตัวอย่างการ Transform ด้วย JOIN

ตัวอย่างการสร้างชุดข้อมูลสำหรับวิเคราะห์ยอดขาย โดยการเชื่อมโยงข้อมูลระหว่าง Fact Tables และ Dimension Tables:

```python
sales_analysis = con.execute("""
SELECT
    oi.order_id,
    oi.product_id,
    p.category_id,
    p.supplier_id,
    o.customer_id,
    o.store_id,
    o.order_date,
    o.promotion_id,
    oi.qty,
    oi.price,
    oi.sales_amount
FROM fact_order_items oi
JOIN fact_orders o
    ON oi.order_id = o.order_id
JOIN dim_product p
    ON oi.product_id = p.product_id
""").df()

## 1.11 Data Cleaning and Transformation Rules

กฎเกณฑ์และมาตรฐานในการจัดการและแปลงสภาพข้อมูล (Transformation Rules):

| รายการ (Item) | กฎการจัดการข้อมูล (Rules) |
| :--- | :--- |
| **Missing Value** | ตรวจสอบและจัดการค่าว่างในทุก Column |
| **Duplicate** | ตรวจสอบและกำจัดข้อมูลที่ซ้ำซ้อน (Duplicate Records) |
| **Primary Key** | ตรวจสอบ Uniqueness (ต้องไม่มีค่าซ้ำ) |
| **Foreign Key** | ตรวจสอบความสัมพันธ์และความสมบูรณ์ของข้อมูลระหว่างตาราง |
| **Date** | แปลงชนิดข้อมูลเป็น `DATE` |
| **Quantity** | กำหนดชนิดข้อมูลเป็น `INTEGER` |
| **Price** | กำหนดชนิดข้อมูลเป็น `NUMERIC` |
| **Discount** | กำหนดชนิดข้อมูลเป็น `NUMERIC` |
| **Status** | กำหนดชนิดข้อมูลเป็น `VARCHAR` / `STRING` |
| **Sales Amount** | คำนวณจากสูตร $Qty \times Price$ |
| **Surrogate Key** | สร้าง SK ขึ้นใหม่สำหรับ Dimension Tables ด้วย `ROW_NUMBER()` |

1.12 การตรวจสอบ Primary Keyสคริปต์สำหรับตรวจสอบความถูกต้องของ Primary Key ในแต่ละ Staging Table ว่าไม่มีค่าซ้ำ:Pythonprimary_keys = {
    'employees': 'employee_id',
    'returns': 'return_id',
    'products': 'product_id',
    'suppliers': 'supplier_id',
    'categories': 'category_id',
    'promotions': 'promotion_id',
    'stores': 'store_id',
    'customers': 'customer_id',
    'payments': 'payment_id',
    'orders': 'order_id',
    'order_items': 'order_item_id',
    'shipments': 'shipment_id'
}

for table, pk in primary_keys.items():
    result = con.execute(f"""
        SELECT {pk}, COUNT(*) AS count
        FROM stg_{table}
        GROUP BY {pk}
        HAVING COUNT(*) > 1
    """).df()

    print(f"{table:15} | Duplicate PK = {len(result):,}")
หมายเหตุ: หากผลลัพธ์แสดง Duplicate PK = 0 แสดงว่า Primary Key ของตารางนั้นๆ มีความถูกต้องและไม่พบรายการซ้ำ

1.13 การตรวจสอบ Foreign Keyตัวอย่างการตรวจสอบ Referential Integrity เพื่อเช็กว่า customer_id ในตาราง fact_orders มีตัวตนอยู่ในตาราง
dim_customer หรือไม่:

Pythonresult = con.execute("""
SELECT COUNT(*) AS invalid_customer
FROM fact_orders o
LEFT JOIN dim_customer c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
""").df()

display(result)
หมายเหตุ: หากผลลัพธ์ invalid_customer เท่ากับ 0 แสดงว่า customer_id ในรายการสั่งซื้อสามารถเชื่อมโยงกับข้อมูลลูกค้าได้ครบถ้วนถูกต้อง


1.14 การตรวจสอบผลลัพธ์ของ Dimension และ Fact Tablesสคริปต์สำหรับตรวจสอบจำนวน Records ทั้งหมดในตาราง Dimension และ Fact หลังจากการ Transform:Pythonfinal_tables = [
    'dim_customer',
    'dim_product',
    'dim_store',
    'dim_category',
    'dim_supplier',
    'dim_promotion',
    'dim_employee',
    'fact_orders',
    'fact_order_items',
    'fact_payments',
    'fact_shipments',
    'fact_returns'
]

for table in final_tables:
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table:20} : {count:,} records")


1.15 ELT Data Flowโครงสร้างและเส้นทางการไหลของข้อมูล (Data Architecture) แบ่งออกเป็น 4 Layer หลัก:[ Layer 1: Source Layer ]
  Google Drive (12 CSV Files)
        │
        ├── employees.csv, returns.csv, products.csv, suppliers.csv, categories.csv,
        └── promotions.csv, stores.csv, customers.csv, payments.csv, orders.csv, ...
        │
        ▼
[ Layer 2: Raw / Staging Layer ]
  DuckDB Persistent Storage
        │
        ├── stg_employees, stg_returns, stg_products, stg_suppliers, stg_categories,
        └── stg_promotions, stg_stores, stg_customers, stg_payments, stg_orders, ...
        │
        ▼
[ Layer 3: Transform Layer ]
  Data Processing & Cleaning
        │
        ├── Cleaning ──► Data Type Conversion ──► Duplicate Check
        └── Key Validation ──► Join ──► Calculations (qty * price)
        │
        ▼
[ Layer 4: Data Warehouse Layer ]
  Star Schema Architecture
        │
        ├─► DIMENSION: Customer, Product, Store, Category, Supplier, Promotion, Employee
        └─► FACT     : Orders, OrderItems, Payments, Shipments, Returns

## 1.16 ตารางสรุปแต่ละ Layer

| Layer | หน้าที่และความรับผิดชอบ | ตัวอย่างออบเจกต์ |
| :--- | :--- | :--- |
| **Source Layer** | จัดเก็บไฟล์ข้อมูลดิบต้นทาง | ไฟล์ CSV บน Google Drive |
| **Raw / Staging Layer** | จัดเก็บข้อมูลดิบที่โหลดเข้าฐานข้อมูล DuckDB โดยตรง | `stg_orders`, `stg_products` |
| **Transform Layer** | ดำเนินการทำความสะอาด, เปลี่ยนชนิดข้อมูล, JOIN และคำนวณ Business Logic | SQL Scripts, `qty * price` |
| **Dimension Layer** | จัดเก็บข้อมูลรายละเอียดและคุณลักษณะรายมิติของธุรกิจ | `dim_product`, `dim_customer` |
| **Fact Layer** | จัดเก็บข้อมูลธุรกรรมและตัวเลขวัดผลเชิงปริมาณ | `fact_orders`, `fact_order_items` |
| **Analysis Layer** | นำเสนอชุดข้อมูลที่ผ่านการ Transform แล้วไปใช้งานต่อในระบบ BI หรือ Analysis | Sales Analysis DataFrame |


## 1.17 Summary of ELT

กระบวนการ **ELT (Extract, Load, Transform)** ของโครงงานเริ่มต้นจากขั้นตอน **Extract** โดยการดึงข้อมูลจากไฟล์ CSV จำนวน 12 ตาราง (`employees`, `returns`, `products`, `suppliers`, `categories`, `promotions`, `stores`, `customers`, `payments`, `orders`, `order_items` และ `shipments`) รวมทั้งสิ้น **1,631,380 Records** และ **39 Columns** จาก Google Drive เข้าสู่ Google Colab ด้วย Python และ Pandas

ถัดมาเป็นขั้นตอน **Load** โดยการนำข้อมูลดิบเข้าสู่ฐานข้อมูล **DuckDB** ในรูปแบบ Staging Tables (ตั้งชื่อนำหน้าด้วย `stg_` เช่น `stg_orders`, `stg_products`) เพื่อทำ Data Persistence และใช้เป็นพื้นที่พักข้อมูลสำหรับตรวจสอบคุณภาพก่อนเข้าสู่กระบวนการถัดไป

ในขั้นตอน **Transform** ได้ทำการตรวจสอบและทำความสะอาดข้อมูล (Data Cleaning) ได้แก่ การตรวจหา Missing Values, Duplicate Records, การทำ Primary/Foreign Key Validation, การแปลงชนิดข้อมูลวันที่ (`DATE`) รวมถึงการสร้าง Business Metric ใหม่ เช่น `sales_amount` ($Qty \times Price$) จากนั้นจึงจัดโครงสร้างข้อมูลให้อยู่ในรูป **Star Schema** ประกอบด้วย 7 Dimension Tables และ 5 Fact Tables

Google Drive (Source)
│
▼
CSV Dataset
│
▼  [ EXTRACT ] (Python + Pandas)
│
RAW / STAGING (DuckDB)
│
▼  [ LOAD ]
│
DuckDB
│
▼  [ TRANSFORM ] (SQL + DuckDB)
├─► Cleaning & Validation (Missing / Duplicates / Keys)
├─► Data Type Conversion (DATE, NUMERIC, etc.)
├─► Joins & Calculations (sales_amount = qty * price)
│
▼
DIMENSION + FACT TABLES
│
▼
DATA WAREHOUSE
│
▼
DATA ANALYSIS


---

## 1.18 สรุปผลการดำเนินงาน

ตารางสรุปรายละเอียดและผลลัพธ์จากการดำเนินงานกระบวนการ ELT:

| หัวข้อ (Metrics) | ผลการดำเนินงาน (Results) |
| :--- | :--- |
| **แหล่งข้อมูล (Source)** | Google Drive |
| **รูปแบบข้อมูล (Format)** | CSV Files |
| **จำนวนตารางต้นทาง** | 12 ตาราง |
| **จำนวน Records รวม** | 1,631,380 Records |
| **จำนวน Columns รวม** | 39 Columns |
| **Extract Tool** | Python + Pandas |
| **Database Engine** | DuckDB |
| **Load Layer** | Raw / Staging |
| **จำนวน Staging Tables** | 12 Tables (`stg_*`) |
| **Transform Tool** | SQL + DuckDB |
| **Data Cleaning** | ตรวจสอบ Missing Values, Duplicates และ Integrity Keys |
| **Data Type Management** | ตรวจสอบและแปลง Data Type ให้เหมาะสมกับการใช้งาน |
| **Dimension Tables** | `Customer`, `Product`, `Store`, `Category`, `Supplier`, `Promotion`, `Employee` (7 Tables) |
| **Fact Tables** | `Orders`, `Order Items`, `Payments`, `Shipments`, `Returns` (5 Tables) |
| **Key Calculation** | `sales_amount = qty * price` |
| **Output Final** | Data Warehouse (Star Schema) พร้อมสำหรับการวิเคราะห์เชิงธุรกิจ |

---

### **ข้อสรุปสำคัญ (Key Takeaways)**

กระบวนการ ELT ที่พัฒนาขึ้นสามารถดึงและโหลดข้อมูลระบบค้าปลีกจากไฟล์ CSV จำนวน 12 ตาราง เข้าสู่ DuckDB ผ่าน **Staging Layer** ได้อย่างมีประสิทธิภาพ จากนั้นได้ดำเนินการทำความสะอาดและแปลงสภาพข้อมูล (Data Transformation) ทั้งการจัดการค่าว่าง, รายการซ้ำ, การตรวจสอบความสัมพันธ์ของ Key และ Data Types ก่อนจัดโครงสร้างออกเป็น **Dimension และ Fact Tables** ตามสถาปัตยกรรม Data Warehouse ซึ่งช่วยให้ข้อมูลมีความถูกต้อง สมบูรณ์ และพร้อมนำไปใช้ในการวิเคราะห์ข้อมูลเชิงลึก (Business Intelligence & Data Analytics) ต่อไป


```
<img width="1125" height="1456" alt="lt1 1" src="https://github.com/user-attachments/assets/43f58282-3ca8-4d84-8b17-75b9f5c17eca" />
<img width="1125" height="1456" alt="lt2" src="https://github.com/user-attachments/assets/63833c61-b31f-40c4-b99f-eca40e4b8025" />
<img width="1125" height="1456" alt="lt3" src="https://github.com/user-attachments/assets/58e66a30-0e61-4a10-9b6b-84d7d885ed25" />
<img width="1125" height="1456" alt="lt4" src="https://github.com/user-attachments/assets/1276d3e2-38bf-4f89-8260-43afc5a503ea" />
<img width="1125" height="1456" alt="it5" src="https://github.com/user-attachments/assets/7a5aca64-7378-412e-bf90-439a58451b6a" />
