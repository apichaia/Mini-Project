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

### 1. Dataset & Operational Database
ความหมายของ Dataset

1. Dataset คือชุดข้อมูลที่นำมาใช้ในการทำโครงงาน โดย Dataset นี้เป็นข้อมูลเกี่ยวกับ การขายสินค้าและการดำเนินงานของร้านค้าปลีก (Retail) ซึ่งประกอบด้วยข้อมูลลูกค้า สินค้า ร้านค้า คำสั่งซื้อ การชำระเงิน การจัดส่ง และการคืนสินค้า

2. Dataset นี้เป็นข้อมูลของ ระบบการขายสินค้าของธุรกิจค้าปลีก โดยจำลองกระบวนการตั้งแต่ลูกค้าเข้ามาสั่งซื้อสินค้า จนถึงการชำระเงิน การจัดส่ง และการคืนสินค้า
ตารางหลักของ Dataset

| ลำดับ	| 	ตาราง	 | จำนวน Records	| จำนวน Columns	| 	รายละเอียด 	|
|-------|------------|------------------|-------------------|---------------|
|   1	|  employees |	1,000		    |	   3	        |   ข้อมูลพนักงาน |


2	   returns 	    30,000	           3	          ข้อมูลการคืนสินค้า
3	   products	    10,000	           4	          ข้อมูลสินค้า
4	   suppliers	200 	           2	          ข้อมูลผู้จัดจำหน่าย
5	   categories	30	               2	          ข้อมูลประเภทสินค้า
6	   promotions	50  	           2	          ข้อมูลโปรโมชั่น
7	   stores	    100 	           2	          ข้อมูลสาขา
8	   customers	50,000	           3	          ข้อมูลลูกค้า
9	   payments 	300,000	           3	          ข้อมูลการชำระเงิน
10	   orders	    300,000	           5	          ข้อมูลคำสั่งซื้อ
11	   order_items	600,000	           5	          รายละเอียดสินค้าในคำสั่งซื้อ
12	   shipments	300,000	           3	          ข้อมูลการจัดส่ง

Dataset หลักทั้ง 12 ตารางมีข้อมูลรวมทั้งหมด 1,631,380 Records และ 39 Columns

https://colab.research.google.com/drive/1cb03m3na2yEKvnH9-JK1oxXGFHjB0PGo#scrollTo=b8417809

3. OLTP (Online Transaction Processing)

OLTP (Online Transaction Processing) หรือ ระบบประมวลผลรายการธุรกรรมออนไลน์ เป็นระบบฐานข้อมูลที่ใช้สำหรับจัดเก็บและประมวลผลธุรกรรมที่เกิดขึ้นจากการดำเนินงานประจำวันขององค์กร โดยมีจุดมุ่งหมายเพื่อให้สามารถบันทึก แก้ไข และเรียกใช้ข้อมูลธุรกรรมได้อย่างรวดเร็ว ถูกต้อง และเป็นระบบ รวมถึงสามารถรองรับธุรกรรมจำนวนมากและการทำงานของผู้ใช้งานหลายคนพร้อมกัน

สำหรับ Dataset ที่นำมาใช้ในโครงงานนี้ มีลักษณะเป็นข้อมูลของ ระบบธุรกิจค้าปลีก (Retail Business) ซึ่งประกอบด้วยข้อมูลลูกค้า สินค้า ร้านค้า พนักงาน ผู้จัดจำหน่าย ประเภทสินค้า โปรโมชั่น ตลอดจนข้อมูลการสั่งซื้อ การชำระเงิน การจัดส่ง และการคืนสินค้า โดย Dataset หลักประกอบด้วย 12 ตาราง จำนวนรวม 1,631,380 Records และ 39 Columns

จากการศึกษาลักษณะและโครงสร้างของข้อมูล พบว่า Dataset มีความสอดคล้องกับระบบ OLTP เนื่องจากมีทั้ง ข้อมูลหลัก (Master Data) และ ข้อมูลธุรกรรม (Transaction Data) ซึ่งทำงานเชื่อมโยงกันเพื่อรองรับกระบวนการขายสินค้า

3.1 ข้อมูลหลัก (Master Data)

ข้อมูลหลักเป็นข้อมูลที่ใช้ประกอบการทำธุรกรรมและไม่ได้เกิดขึ้นใหม่ทุกครั้งที่มีการซื้อสินค้า ประกอบด้วยตารางต่าง ๆ ดังนี้

-`customers     ใช้จัดเก็บข้อมูลลูกค้า      เช่น customer_id, city และ signup_date มีจำนวน 50,000 Records`
-`products      ใช้จัดเก็บข้อมูลสินค้า      เช่น product_id, category_id, supplier_id และ price มีจำนวน 10,000 Records`
-categories    ใช้จัดเก็บประเภทสินค้า         มีจำนวน 30 Records
-suppliers     ใช้จัดเก็บข้อมูลผู้จัดจำหน่าย     มีจำนวน 200 Records
-stores        ใช้จัดเก็บข้อมูลสาขา          มีจำนวน 100 Records
-employees     ใช้จัดเก็บข้อมูลพนักงาน        มีจำนวน 1,000 Records
-promotions    ใช้จัดเก็บข้อมูลโปรโมชั่น       มีจำนวน 50 Records

ข้อมูลเหล่านี้จะถูกนำมาใช้ประกอบการทำธุรกรรม เช่น เมื่อมีการสั่งซื้อสินค้า ระบบจะนำข้อมูลลูกค้า สินค้า สาขา และโปรโมชั่นที่เกี่ยวข้องมาเชื่อมโยงกับคำสั่งซื้อ

3.2 ข้อมูลธุรกรรม (Transaction Data)

ข้อมูลธุรกรรมเป็นข้อมูลที่เกิดขึ้นจากกิจกรรมต่าง ๆ ของระบบ โดยมีการเพิ่มข้อมูลเมื่อเกิดเหตุการณ์ใหม่ เช่น การสั่งซื้อ การชำระเงิน หรือการจัดส่ง ประกอบด้วย

orders ใช้บันทึกข้อมูลคำสั่งซื้อ ประกอบด้วย order_id, customer_id, store_id, order_date และ promotion_id มีจำนวน 300,000 Records
order_items ใช้บันทึกรายละเอียดสินค้าในแต่ละคำสั่งซื้อ ประกอบด้วย order_item_id, order_id, product_id, qty และ price มีจำนวน 600,000 Records
payments ใช้บันทึกข้อมูลการชำระเงิน ประกอบด้วย payment_id, order_id และ amount มีจำนวน 300,000 Records
shipments ใช้บันทึกข้อมูลการจัดส่ง ประกอบด้วย shipment_id, order_id และ status มีจำนวน 300,000 Records
returns ใช้บันทึกข้อมูลการคืนสินค้า ประกอบด้วย return_id, order_item_id และ refund มีจำนวน 30,000 Records

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



## 2. ER Diagram (หลิน) 
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

## 3.Business Questions (ฟีฟ่า)


## 4. Business Process and Multidimensional Data Model

### 4.1 Business Process

จากการวิเคราะห์ระบบขายปลีก พบว่าข้อมูลสามารถแบ่งออกเป็นกระบวนการทางธุรกิจหลักที่เกี่ยวข้องกับการวิเคราะห์ใน Dashboard ดังนี้

#### 1. Sales Process

กระบวนการขายสินค้าเป็น Business Process หลักของระบบ โดยใช้ข้อมูลจาก `Orders` และ `Order Items` เพื่อวิเคราะห์ยอดขาย จำนวนสินค้าที่ขาย รายได้ตามสินค้า หมวดหมู่ ลูกค้า ร้านค้า โปรโมชั่น และซัพพลายเออร์

ข้อมูลหลักที่เกี่ยวข้อง:
- `Orders`
- `Order Items`
- `Products`
- `Categories`
- `Customers`
- `Stores`
- `Promotions`
- `Suppliers`

ตัวชี้วัดสำคัญ:
- Total Sales / Revenue
- Monthly Revenue
- Product Revenue
- Units Sold
- Category Revenue
- Store Revenue
- Customer Revenue
- Average Order Value (AOV)
- Sales Growth Rate
- Promotion Revenue
- Supplier Revenue

Grain ของ Sales Process:

> 1 แถวใน Fact_Sales แทนสินค้า 1 รายการใน 1 Order Line Item (One Order Line Item)


#### 2. Return Process

กระบวนการคืนสินค้าใช้ข้อมูลจาก `Returns` ซึ่งเชื่อมโยงกับ `Order Items` เพื่อวิเคราะห์จำนวนและมูลค่าการคืนสินค้า รวมถึงใช้เปรียบเทียบกับยอดขายเพื่อคำนวณ Return Rate

ข้อมูลหลักที่เกี่ยวข้อง:
- `Returns`
- `Order Items`
- `Orders`
- `Products`
- `Customers`
- `Stores`

ตัวชี้วัดสำคัญ:
- Returned Quantity
- Refund Amount
- Return Rate

Grain ของ Return Process:

> 1 แถวใน Fact_Returns แทน 1 รายการการคืนสินค้า (One Return Transaction)

หมายเหตุ: ตาราง `Returns` ในระบบไม่มีข้อมูลสาเหตุการคืนสินค้า (`return_reason`) ดังนั้นไม่สามารถวิเคราะห์ Return Rate by Reason ได้จากข้อมูลปัจจุบัน


#### 3. Shipment Process

กระบวนการจัดส่งสินค้าใช้ข้อมูลจาก `Shipments` ซึ่งเชื่อมโยงกับ `Orders` เพื่อวิเคราะห์สถานะของการจัดส่งสินค้า

ข้อมูลหลักที่เกี่ยวข้อง:
- `Shipments`
- `Orders`
- `Customers`
- `Stores`

ตัวชี้วัด/ข้อมูลที่สามารถวิเคราะห์ได้:
- Shipment Status
- จำนวน Shipment ตามสถานะ
- สัดส่วน Shipment ตามสถานะ

Grain ของ Shipment Process:

> 1 แถวใน Fact_Shipments แทน 1 รายการจัดส่งสินค้า (One Shipment)

หมายเหตุ: ตาราง `Shipments` มีเพียง `shipment_id`, `order_id` และ `status` ไม่มีข้อมูลวันที่คาดว่าจะจัดส่งหรือวันที่จัดส่งจริง ดังนั้นจึงไม่สามารถคำนวณ On-Time Delivery Rate หรือ Average Delivery Time ได้จากข้อมูลปัจจุบัน


#### 4. Payment Process

กระบวนการชำระเงินใช้ข้อมูลจาก `Payments` ซึ่งเชื่อมโยงกับ `Orders` เพื่อวิเคราะห์จำนวนเงินที่ชำระในแต่ละรายการ

ข้อมูลหลักที่เกี่ยวข้อง:
- `Payments`
- `Orders`

ตัวชี้วัดสำคัญ:
- Payment Amount
- Number of Payment Transactions

Grain ของ Payment Process:

> 1 แถวใน Fact_Payments แทน 1 รายการธุรกรรมการชำระเงิน (One Payment Transaction)

หมายเหตุ: ตาราง `Payments` ไม่มีข้อมูล `payment_method` ดังนั้นไม่สามารถวิเคราะห์ Payment Method Usage ตามประเภทวิธีการชำระเงินได้จากข้อมูลปัจจุบัน.


---

### 4.2 Multidimensional Data Model

จาก Business Process ที่วิเคราะห์ สามารถออกแบบ Multidimensional Data Model โดยแบ่งข้อมูลออกเป็น Fact Tables และ Dimension Tables เพื่อรองรับการวิเคราะห์ข้อมูลใน Dashboard

#### Fact Tables

ระบบประกอบด้วย Fact Tables หลัก 4 ตาราง ได้แก่

##### 1.Fact_Sales

ใช้เก็บข้อมูลเชิงตัวเลขที่เกี่ยวข้องกับการขายสินค้า

**Grain:**
> 1 แถว = 1 สินค้าใน 1 Order Line Item

**Foreign Keys:**
- `date_id`
- `product_id`
- `customer_id`
- `store_id`
- `promotion_id`
- `supplier_id`

**Degenerate/Reference Keys:**
- `order_id`
- `order_item_id`

**Measures:**
- `quantity` — จำนวนสินค้าที่ขาย
- `unit_price` — ราคาต่อหน่วย
- `sales_amount` — มูลค่าการขาย
- `discount` — ส่วนลด

Calculated Measures:
- `Average Selling Price = Sales Amount / Quantity`
- `Sales Growth Rate`
- `Average Order Value (AOV)`
- `Profit Margin` หากมีข้อมูลต้นทุน/กำไรเพิ่มเติมในข้อมูลต้นทาง


##### 2. Fact_Returns

ใช้เก็บข้อมูลการคืนสินค้า

**Grain:**
> 1 แถว = 1 Return Transaction

**Foreign Keys:**
- `product_id`
- `customer_id`
- `store_id`

**Reference Keys:**
- `return_id`
- `order_item_id`

**Measures:**
- `refund` — จำนวนเงินคืนสินค้า
- `returned_quantity` หากสามารถคำนวณหรือมีข้อมูลจำนวนสินค้าที่คืนจากข้อมูลต้นทาง

Calculated Measure:
- `Return Rate = Returned Quantity / Sold Quantity × 100`

หมายเหตุ: ตาราง `Returns` มีเพียง `return_id`, `order_item_id` และ `refund` จึงไม่มีข้อมูล `return_reason` และไม่มีวันที่คืนสินค้าโดยตรง


##### 3. Fact_Shipments

ใช้เก็บข้อมูลการจัดส่งสินค้า

**Grain:**
> 1 แถว = 1 Shipment

**Foreign Keys / Reference Keys:**
- `order_id`
- `customer_id`
- `store_id`

**Measures / Attributes:**
- `status` — สถานะการจัดส่ง

เนื่องจากข้อมูลต้นทางไม่มีวันที่จัดส่งหรือวันที่คาดว่าจะจัดส่ง จึงไม่สามารถคำนวณ Delivery Lead Time และ On-Time Delivery Rate ได้


##### 4. Fact_Payments

ใช้เก็บข้อมูลธุรกรรมการชำระเงิน

**Grain:**
> 1 แถว = 1 Payment Transaction

**Reference Keys:**
- `payment_id`
- `order_id`

**Measure:**
- `amount` — จำนวนเงินที่ชำระ

หมายเหตุ: ไม่มี `payment_method` ในตาราง Payments ดังนั้นไม่สามารถวิเคราะห์การใช้งานวิธีการชำระเงินแต่ละประเภทได้

---

### 4.3 Dimension Tables

#### Dim_Date

ใช้สำหรับวิเคราะห์ข้อมูลตามช่วงเวลา

**Primary Key:**
- `date_id`

**Attributes:**
- `day`
- `month`
- `quarter`
- `year`

Hierarchy:

> Year → Quarter → Month → Day

ใช้สำหรับการวิเคราะห์:
- Daily Sales
- Monthly Revenue
- Quarterly Revenue
- Yearly Revenue
- Sales Growth Rate


#### Dim_Product

ใช้สำหรับวิเคราะห์ข้อมูลตามสินค้าและหมวดหมู่สินค้า

**Primary Key:**
- `product_id`

**Attributes:**
- `category_id`
- `category_name`
- `supplier_id`
- `price`

โดยข้อมูล `category_name` มาจากตาราง `Categories` และนำมารวมไว้ใน Dim_Product เพื่อให้โครงสร้างสามารถรองรับ Star Schema ได้โดยไม่ต้องเชื่อมต่อ Dimension ผ่าน Dimension อีกชั้นหนึ่ง


#### Dim_Customer

ใช้สำหรับวิเคราะห์พฤติกรรมและรายได้ของลูกค้า

**Primary Key:**
- `customer_id`

**Attributes:**
- `city`
- `signup_date`


#### Dim_Store

ใช้สำหรับวิเคราะห์ผลการดำเนินงานของแต่ละสาขา

**Primary Key:**
- `store_id`

**Attributes:**
- `city`

Hierarchy:

> Store → City


#### Dim_Promotion

ใช้สำหรับวิเคราะห์ผลของโปรโมชั่นต่อยอดขาย

**Primary Key:**
- `promotion_id`

**Attributes:**
- `discount`

ใช้ในการวิเคราะห์:
- Promotion Revenue
- Promotion Performance
- Promotion Lift


#### Dim_Supplier

ใช้สำหรับวิเคราะห์ข้อมูลของ Supplier

**Primary Key:**
- `supplier_id`

**Attributes:**
- `country`

ใช้ในการวิเคราะห์ Supplier Revenue


#### Dim_Employee

ใช้สำหรับวิเคราะห์ข้อมูลพนักงานและความสัมพันธ์กับสาขา

**Primary Key:**
- `employee_id`

**Attributes:**
- `store_id`
- `salary`

หมายเหตุ: ใน ER Diagram พนักงานเชื่อมโยงกับ Store แต่ไม่มีความสัมพันธ์โดยตรงกับ Orders ดังนั้นไม่สามารถใช้ข้อมูลนี้เพื่อคำนวณ Sales per Employee ได้โดยตรง

### 4.3 Measures and Measure Types

Measures คือค่าตัวเลขที่ใช้ในการวิเคราะห์ข้อมูลใน Fact Tables โดยสามารถแบ่งตามลักษณะการนำไปคำนวณรวมได้เป็น Additive, Semi-Additive และ Non-Additive Measures

#### 1. Fact_Sales Measures

| Measure | Description | Measure Type |
|---|---|---|
| `quantity` | จำนวนสินค้าที่ขายในแต่ละ Order Line Item | Additive |
| `sales_amount` | มูลค่าการขายสินค้า | Additive |
| `unit_price` | ราคาขายต่อหน่วย | Non-Additive |
| `discount` | มูลค่าส่วนลดจาก Promotion | Additive |

Calculated Measures:

| Calculated Measure | Formula | Measure Type |
|---|---|---|
| `Total Sales` | SUM(sales_amount) | Additive |
| `Units Sold` | SUM(quantity) | Additive |
| `Average Selling Price` | SUM(sales_amount) / SUM(quantity) | Non-Additive |
| `Average Order Value (AOV)` | SUM(sales_amount) / COUNT(DISTINCT order_id) | Non-Additive |
| `Sales Growth Rate` | ((Current Sales - Previous Sales) / Previous Sales) × 100 | Non-Additive |
| `Promotion Revenue` | SUM(sales_amount) GROUP BY promotion_id | Additive |
| `Supplier Revenue` | SUM(sales_amount) GROUP BY supplier_id | Additive |


#### 2. Fact_Returns Measures

| Measure | Description | Measure Type |
|---|---|---|
| `refund` | จำนวนเงินที่คืนให้ลูกค้า | Additive |

Calculated Measures:

| Calculated Measure | Formula | Measure Type |
|---|---|---|
| `Total Refund` | SUM(refund) | Additive |
| `Return Rate` | Returned Transactions / Total Sales Transactions × 100 | Non-Additive |

หมายเหตุ: เนื่องจากตาราง `Returns` ไม่มี `returned_quantity` จึงไม่สามารถคำนวณ Return Rate จากจำนวนชิ้นสินค้าได้โดยตรง หากต้องการคำนวณ Return Rate ตามจำนวนสินค้า จำเป็นต้องมีข้อมูลจำนวนสินค้าที่คืนเพิ่มเติม


#### 3. Fact_Shipments Measures

| Measure | Description | Measure Type |
|---|---|---|
| `shipment_count` | จำนวนรายการจัดส่ง | Additive |

Calculated Measures:

| Calculated Measure | Formula | Measure Type |
|---|---|---|
| `Shipment Count` | COUNT(shipment_id) | Additive |
| `Shipment Status Rate` | Shipment Count by Status / Total Shipment Count × 100 | Non-Additive |

หมายเหตุ: ตาราง `Shipments` มีเพียง `shipment_id`, `order_id` และ `status` จึงสามารถวิเคราะห์จำนวนและสัดส่วนตามสถานะได้ แต่ไม่สามารถคำนวณ Delivery Lead Time หรือ On-Time Delivery Rate ได้


#### 4. Fact_Payments Measures

| Measure | Description | Measure Type |
|---|---|---|
| `amount` | จำนวนเงินที่ชำระ | Additive |

Calculated Measures:

| Calculated Measure | Formula | Measure Type |
|---|---|---|
| `Total Payment Amount` | SUM(amount) | Additive |
| `Payment Transaction Count` | COUNT(payment_id) | Additive |

หมายเหตุ: ตาราง `Payments` ไม่มี `payment_method` จึงไม่สามารถวิเคราะห์ Payment Method Usage ตามประเภทวิธีการชำระเงินได้

---

### 4.5 Summary of Fact and Dimension Tables

#### Fact Tables

| Table | Grain / Purpose | Base Measures | Measure Type | Calculated Measures |
|---|---|---|---|---|
| `Fact_Sales` | 1 Order Line Item | `quantity`, `sales_amount`, `discount`, `unit_price` | Additive: `quantity`, `sales_amount`, `discount` / Non-Additive: `unit_price` | `Average Selling Price`, `AOV`, `Sales Growth Rate`, `Promotion Revenue`, `Supplier Revenue` |
| `Fact_Returns` | 1 Return Transaction | `refund` | Additive | `Total Refund`, `Return Rate*` |
| `Fact_Shipments` | 1 Shipment | `shipment_count` | Additive | `Shipment Status Rate` |
| `Fact_Payments` | 1 Payment Transaction | `amount` | Additive | `Total Payment Amount`, `Payment Transaction Count` |


#### Dimension Tables

| Table | Type | Primary Key | Main Attributes | Purpose |
|---|---|---|---|---|
| `Dim_Date` | Dimension | `date_id` | `day`, `month`, `quarter`, `year` | วิเคราะห์ข้อมูลตามช่วงเวลา |
| `Dim_Product` | Dimension | `product_id` | `category_id`, `category_name`, `supplier_id`, `price` | วิเคราะห์สินค้าและหมวดหมู่ |
| `Dim_Customer` | Dimension | `customer_id` | `city`, `signup_date` | วิเคราะห์ลูกค้าและพฤติกรรมการซื้อ |
| `Dim_Store` | Dimension | `store_id` | `city` | วิเคราะห์ยอดขายตามสาขา |
| `Dim_Promotion` | Dimension | `promotion_id` | `discount` | วิเคราะห์ประสิทธิภาพของ Promotion |
| `Dim_Supplier` | Dimension | `supplier_id` | `country` | วิเคราะห์ Supplier และรายได้จากสินค้า |
| `Dim_Employee` | Dimension | `employee_id` | `store_id`, `salary` | วิเคราะห์ข้อมูลพนักงานและสาขา |


---

### 4.6 Overall Multidimensional Model

Multidimensional Data Model ของระบบประกอบด้วยหลาย Fact Tables ที่ใช้ Dimension ร่วมกัน โดย `Fact_Sales` เป็น Fact หลักสำหรับการวิเคราะห์ยอดขาย และมี `Fact_Returns`, `Fact_Shipments` และ `Fact_Payments` สำหรับรองรับกระบวนการคืนสินค้า การจัดส่ง และการชำระเงินตามลำดับ

Dimension ที่สามารถใช้ร่วมกันระหว่างหลาย Fact Tables ได้แก่ `Dim_Date`, `Dim_Product`, `Dim_Customer` และ `Dim_Store` ซึ่งช่วยให้สามารถวิเคราะห์ข้อมูลจากหลาย Business Processes ในมุมมองเดียวกัน

โครงสร้างโดยรวมสามารถอธิบายได้ว่าเป็น **Fact Constellation / Galaxy Schema** ซึ่งประกอบด้วยหลาย Star Schemas ที่ใช้ Conformed Dimensions ร่วมกัน

```text
                         Dim_Date
                       /     |      \
                      /      |       \
                     ▼       ▼        ▼
              Fact_Sales  Fact_Returns  Fact_Shipments
                  │           │             │
             Dimensions   Dimensions    Dimensions
                  │
                  ▼
             Fact_Payments

```

### Data Model Diagram (Star Scheme) แซนด์วิช
<img src="./readme_images/StarSchema1.jpg">

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
<1,591,380 Records และ 39 Columns>

# 2 ELT Process

## 2.1 Extract

ขั้นตอน Extract เป็นการดึงข้อมูลจาก Source Data ซึ่งประกอบด้วยไฟล์ CSV จำนวน 12 ตาราง ได้แก่ `employees`, `returns`, `products`, `suppliers`, `categories`, `promotions`, `stores`, `customers`, `payments`, `orders`, `order_items` และ `shipments`

ข้อมูลถูกอ่านเข้าสู่ Python โดยใช้ Pandas DataFrame เพื่อเตรียมเข้าสู่กระบวนการ Load โดยข้อมูลต้นทางประกอบด้วยข้อมูลการขาย ลูกค้า สินค้า Supplier Promotion การชำระเงิน การจัดส่ง และการคืนสินค้า

### Extract Process

```text
Google Drive
     │
     ▼
CSV Files จำนวน 12 ตาราง
     │
     ▼
Python + Pandas
     │
     ▼
Loaded DataFrames
```

---

## 1.2 Load

หลังจาก Extract ข้อมูลจาก CSV แล้ว ข้อมูลจะถูก Load เข้าสู่ฐานข้อมูล DuckDB โดยสร้างเป็น Staging Tables ซึ่งใช้ชื่อในรูปแบบ `stg_<table_name>` เช่น `stg_orders`, `stg_products`, `stg_customers`

Staging Layer มีหน้าที่เก็บข้อมูลจาก Source ก่อนเข้าสู่ Transformation เพื่อให้สามารถตรวจสอบ Missing Values, Duplicate Records, Data Types และ Referential Integrity ได้ก่อนนำไปสร้าง Data Warehouse

### Load Process

```text
Pandas DataFrame
       │
       ▼
     DuckDB
       │
       ▼
Staging Tables
       │
       ├── stg_employees
       ├── stg_returns
       ├── stg_products
       ├── stg_suppliers
       ├── stg_categories
       ├── stg_promotions
       ├── stg_stores
       ├── stg_customers
       ├── stg_payments
       ├── stg_orders
       ├── stg_order_items
       └── stg_shipments
```

---

# 2.3 Transform

ขั้นตอน Transform เป็นการนำข้อมูลจาก Staging Layer มาทำความสะอาด ตรวจสอบชนิดข้อมูล JOIN ตาราง และคำนวณ Business Measures ก่อนจัดโครงสร้างเป็น Dimension Tables และ Fact Tables ตาม Data Model Diagram

## 1.3.1 Transform Dimension Tables

จาก Data Model ที่กำหนด ประกอบด้วย Dimension Tables จำนวน 6 ตาราง ได้แก่

1. `Dim_Date`
2. `Dim_Product`
3. `Dim_Customer`
4. `Dim_Store`
5. `Dim_Promotion`
6. `Dim_Supplier`

### Dim_Date

`Dim_Date` ใช้สำหรับเก็บรายละเอียดของวันที่ ได้แก่ `date_id`, `year`, `quarter`, `month` และ `day` โดยสร้างจาก `order_date` ที่อยู่ใน `stg_orders`

### Dim_Product

`Dim_Product` เก็บรายละเอียดสินค้า ได้แก่ `product_id`, `category_id`, `supplier_id` และ `price`

### Dim_Customer

`Dim_Customer` เก็บข้อมูลลูกค้า ได้แก่ `customer_id`, `city` และ `signup_date`

### Dim_Store

`Dim_Store` เก็บข้อมูลสาขา ได้แก่ `store_id` และ `city`

### Dim_Promotion

`Dim_Promotion` เก็บข้อมูล Promotion ได้แก่ `promotion_id` และ `discount`

### Dim_Supplier

`Dim_Supplier` เก็บข้อมูล Supplier ได้แก่ `supplier_id` และ `country`

---

## 2.3.2 Transform Fact Tables

จาก Data Model Diagram มี Fact Tables จำนวน 4 ตาราง ได้แก่

1. `Fact_Sales`
2. `Fact_Return`
3. `Fact_Shipments`
4. `Fact_Payments`

### Fact_Sales

`Fact_Sales` มี Grain เป็น **1 Order Line Item** โดยรวมข้อมูลจาก `orders`, `order_items`, `products` และ `promotions`

ประกอบด้วย Foreign Keys ได้แก่ `date_id`, `product_id`, `customer_id`, `store_id`, `promotion_id` และ `supplier_id`

Measures ได้แก่

* `quantity`
* `unit_price`
* `sales_amount`
* `discount`

โดย `sales_amount` คำนวณจาก

**sales_amount = quantity × unit_price**

### Fact_Return

`Fact_Return` มี Grain เป็น **1 Return Transaction** โดยเชื่อมโยงข้อมูล Return กับ `order_items` และ `orders` เพื่อหา `date_id`, `product_id`, `customer_id` และ `store_id`

Measure คือ `refund`

### Fact_Shipments

`Fact_Shipments` มี Grain เป็น **1 Shipment** โดยเชื่อมกับ `orders` เพื่อหา `customer_id` และ `store_id`

เก็บข้อมูล `shipment_id`, `customer_id`, `store_id`, `order_id` และ `status`

### Fact_Payments

`Fact_Payments` มี Grain เป็น **1 Payment Transaction** โดยเชื่อมกับ `orders` เพื่อหา `date_id`, `customer_id` และ `store_id`

Measure คือ `amount`

---

# 2.4 Data Cleaning and Transformation Rules

กฎที่ใช้ในการทำความสะอาดและ Transformation ประกอบด้วย

| รายการ        | Data Cleaning / Transformation Rule                      |
| ------------- | -------------------------------------------------------- |
| Missing Value | ตรวจสอบค่าว่างในทุก Column                               |
| Duplicate     | ตรวจสอบข้อมูลซ้ำและกำจัด Duplicate Records หากพบ         |
| Primary Key   | ตรวจสอบว่า Primary Key ไม่มีค่าซ้ำ                       |
| Foreign Key   | ตรวจสอบ Referential Integrity ระหว่าง Fact และ Dimension |
| Date          | แปลงข้อมูลวันที่เป็น `DATE` ด้วย `TRY_CAST()`            |
| Quantity      | แปลงเป็น `INTEGER`                                       |
| Price         | แปลงเป็น `NUMERIC`                                       |
| Discount      | แปลงเป็น `NUMERIC`                                       |
| Refund        | แปลงเป็น `NUMERIC`                                       |
| Amount        | แปลงเป็น `NUMERIC`                                       |
| Status        | เก็บเป็น `VARCHAR` / `STRING`                            |
| Sales Amount  | คำนวณจาก `quantity × unit_price`                         |
| Date Key      | สร้าง `date_id` จากวันที่เพื่อเชื่อมกับ `Dim_Date`       |

แนวทาง Data Cleaning และ Transformation นี้สอดคล้องกับกฎในโปรเจกต์ต้นฉบับ เช่น Missing Value, Duplicate, Primary/Foreign Key Validation, Date Conversion และการคำนวณ `sales_amount`

---

# 2.5 ELT Data Flow

กระบวนการ ELT ของระบบสามารถแบ่งออกเป็น 4 Layer ได้แก่

```text
┌───────────────────────────────────────┐
│           Layer 1: SOURCE             │
│                                       │
│        Google Drive / CSV             │
│           12 Source Tables            │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│       Layer 2: RAW / STAGING          │
│                                       │
│              DuckDB                  │
│                                       │
│           stg_* Tables                │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│          Layer 3: TRANSFORM            │
│                                       │
│  Cleaning → Type Conversion            │
│  Key Validation → JOIN → Calculation   │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│       Layer 4: DATA WAREHOUSE          │
│                                       │
│          Dimension Tables              │
│              +                        │
│            Fact Tables                 │
│                                       │
│          Star Schema                  │
└───────────────────┬───────────────────┘
                    │
                    ▼
              DATA ANALYSIS
```

โครงสร้างนี้ต่อยอดจาก ELT Data Flow ในโปรเจกต์ต้นฉบับ ซึ่งใช้ Source CSV → DuckDB Staging → Cleaning/Validation → Transformation → Data Warehouse

---

# 2.6 Summary of ELT

กระบวนการ ELT เริ่มจากการ Extract ข้อมูลจาก CSV จำนวน 12 ตารางด้วย Python และ Pandas จากนั้น Load ข้อมูลเข้าสู่ DuckDB ในรูปแบบ Staging Tables จำนวน 12 ตาราง เพื่อใช้เป็นพื้นที่สำหรับ Data Persistence และ Data Quality Checking

ในขั้นตอน Transform มีการตรวจสอบ Missing Values, Duplicate Records, Primary Key, Foreign Key และ Data Types จากนั้นทำการ JOIN ข้อมูลระหว่าง `orders`, `order_items`, `products`, `promotions` และตารางอื่น ๆ เพื่อสร้าง Fact และ Dimension Tables

Final Data Warehouse ตาม Data Model Diagram ประกอบด้วย

### Dimension Tables — 6 Tables

* `Dim_Date`
* `Dim_Product`
* `Dim_Customer`
* `Dim_Store`
* `Dim_Promotion`
* `Dim_Supplier`

### Fact Tables — 4 Tables

* `Fact_Sales`
* `Fact_Return`
* `Fact_Shipments`
* `Fact_Payments`

โดย `Fact_Sales` เป็น Fact หลักสำหรับวิเคราะห์ยอดขาย และมีการคำนวณ `sales_amount = quantity × unit_price`

โครงสร้างสุดท้ายเป็น **Multiple Star Schema / Fact Constellation** ซึ่งมี Fact Tables หลายชุดและใช้ Dimension Tables ร่วมกันในการวิเคราะห์ข้อมูล

```
12 CSV
  ↓
Extract
Python + Pandas
  ↓
Load
DuckDB Staging
  ↓
Transform
Cleaning + Validation + JOIN + Calculation
  ↓
6 Dimensions + 4 Facts
  ↓
Data Warehouse
  ↓
Business Analysis
```

กระบวนการโดยรวมสอดคล้องกับแนวทาง ELT ของโปรเจกต์ต้นฉบับที่ใช้ Python + Pandas, DuckDB, Staging Layer และ SQL Transformation ก่อนสร้าง Data Warehouse

```python3

โค้ด 1.1 Extract
import os
import pandas as pd
import duckdb

# ============================================
# 1.1 EXTRACT
# ============================================

tables = [
    'employees',
    'returns',
    'products',
    'suppliers',
    'categories',
    'promotions',
    'stores',
    'customers',
    'payments',
    'orders',
    'order_items',
    'shipments'
]

loaded_data = {}

for table in tables:
    file_path = os.path.join(path, table + '.csv')

    df = pd.read_csv(file_path)

    loaded_data[table] = df

    print(f"{table}.csv -> {len(df):,} records")
โค้ด 1.2 Load
# ============================================
# 1.2 LOAD TO DUCKDB
# ============================================

db_path = os.path.join(path, 'retail.duckdb')

con = duckdb.connect(db_path)

for table in tables:

    file_path = os.path.join(path, table + '.csv')

    con.execute(f"""
        CREATE OR REPLACE TABLE stg_{table} AS
        SELECT *
        FROM read_csv_auto(?)
    """, [file_path])

    print(f"Loaded: {table}.csv -> stg_{table}")
โค้ด 1.3.1 Transform Dimensions

ตรงนี้ผมปรับให้ตรงกับรูปที่คุณส่งมา โดย ไม่มี dim_category แยก และ category_id อยู่ใน dim_product

# ============================================
# 1.3.1 DIMENSION TABLES
# ============================================

# --------------------------------------------
# DIM DATE
# --------------------------------------------

con.execute("""
CREATE OR REPLACE TABLE dim_date AS
SELECT DISTINCT
    CAST(STRFTIME(TRY_CAST(order_date AS DATE), '%Y%m%d')
         AS INTEGER) AS date_id,

    EXTRACT(YEAR FROM TRY_CAST(order_date AS DATE))
        AS year,

    EXTRACT(QUARTER FROM TRY_CAST(order_date AS DATE))
        AS quarter,

    EXTRACT(MONTH FROM TRY_CAST(order_date AS DATE))
        AS month,

    EXTRACT(DAY FROM TRY_CAST(order_date AS DATE))
        AS day

FROM stg_orders
WHERE TRY_CAST(order_date AS DATE) IS NOT NULL
ORDER BY date_id
""")


# --------------------------------------------
# DIM PRODUCT
# --------------------------------------------

con.execute("""
CREATE OR REPLACE TABLE dim_product AS
SELECT
    product_id,
    category_id,
    supplier_id,
    price
FROM stg_products
""")


# --------------------------------------------
# DIM CUSTOMER
# --------------------------------------------

con.execute("""
CREATE OR REPLACE TABLE dim_customer AS
SELECT
    customer_id,
    city,
    TRY_CAST(signup_date AS DATE) AS signup_date
FROM stg_customers
""")


# --------------------------------------------
# DIM STORE
# --------------------------------------------

con.execute("""
CREATE OR REPLACE TABLE dim_store AS
SELECT
    store_id,
    city
FROM stg_stores
""")


# --------------------------------------------
# DIM PROMOTION
# --------------------------------------------

con.execute("""
CREATE OR REPLACE TABLE dim_promotion AS
SELECT
    promotion_id,
    discount
FROM stg_promotions
""")


# --------------------------------------------
# DIM SUPPLIER
# --------------------------------------------

con.execute("""
CREATE OR REPLACE TABLE dim_supplier AS
SELECT
    supplier_id,
    country
FROM stg_suppliers
""")

print("Dimension Tables created successfully.")
โค้ด 1.3.2 Transform Facts
Fact Sales
# ============================================
# FACT SALES
# Grain: 1 Order Line Item
# ============================================

con.execute("""
CREATE OR REPLACE TABLE fact_sales AS

SELECT
    oi.order_item_id AS order_items_id,

    CAST(
        STRFTIME(
            TRY_CAST(o.order_date AS DATE),
            '%Y%m%d'
        ) AS INTEGER
    ) AS date_id,

    oi.product_id,

    o.customer_id,

    o.store_id,

    o.promotion_id,

    p.supplier_id,

    oi.order_id,

    CAST(oi.qty AS INTEGER) AS quantity,

    CAST(oi.price AS NUMERIC) AS unit_price,

    CAST(
        oi.qty * oi.price
        AS NUMERIC
    ) AS sales_amount,

    CAST(
        COALESCE(pr.discount, 0)
        AS NUMERIC
    ) AS discount

FROM stg_order_items oi

LEFT JOIN stg_orders o
    ON oi.order_id = o.order_id

LEFT JOIN stg_products p
    ON oi.product_id = p.product_id

LEFT JOIN stg_promotions pr
    ON o.promotion_id = pr.promotion_id
""")
Fact Return

เนื่องจาก stg_returns มี return_id, order_item_id, refund จึงต้อง JOIN ผ่าน order_items และ orders เพื่อให้ได้ข้อมูลตาม Diagram

# ============================================
# FACT RETURN
# Grain: 1 Return Transaction
# ============================================

con.execute("""
CREATE OR REPLACE TABLE fact_return AS

SELECT
    r.return_id,

    CAST(
        STRFTIME(
            TRY_CAST(o.order_date AS DATE),
            '%Y%m%d'
        ) AS INTEGER
    ) AS date_id,

    oi.product_id,

    o.customer_id,

    o.store_id,

    r.order_item_id AS order_items_id,

    CAST(r.refund AS NUMERIC) AS refund

FROM stg_returns r

LEFT JOIN stg_order_items oi
    ON r.order_item_id = oi.order_item_id

LEFT JOIN stg_orders o
    ON oi.order_id = o.order_id
""")
Fact Shipments
# ============================================
# FACT SHIPMENTS
# Grain: 1 Shipment
# ============================================

con.execute("""
CREATE OR REPLACE TABLE fact_shipments AS

SELECT
    s.shipment_id AS shipments_id,

    o.customer_id,

    o.store_id,

    s.order_id,

    CAST(s.status AS VARCHAR) AS status

FROM stg_shipments s

LEFT JOIN stg_orders o
    ON s.order_id = o.order_id
""")
Fact Payments
# ============================================
# FACT PAYMENTS
# Grain: 1 Payment Transaction
# ============================================

con.execute("""
CREATE OR REPLACE TABLE fact_payments AS

SELECT
    p.payment_id,

    CAST(
        STRFTIME(
            TRY_CAST(o.order_date AS DATE),
            '%Y%m%d'
        ) AS INTEGER
    ) AS date_id,

    o.customer_id,

    o.store_id,

    p.order_id,

    CAST(p.amount AS NUMERIC) AS amount

FROM stg_payments p

LEFT JOIN stg_orders o
    ON p.order_id = o.order_id
""")
โค้ด 1.4 Data Cleaning & Validation

ส่วนนี้ยึดแนวทางตรวจ Missing Values, Duplicate และ Key Validation จากโปรเจกต์เดิม

ตรวจ Missing Values และ Duplicate
# ============================================
# 1.4 DATA QUALITY CHECK
# ============================================

for table in tables:

    df = con.execute(
        f"SELECT * FROM stg_{table}"
    ).df()

    print("=" * 60)
    print(f"Table: {table}")

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Records:")
    print(df.duplicated().sum())
ตรวจ Primary Key
# ============================================
# PRIMARY KEY VALIDATION
# ============================================

primary_keys = {
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
        SELECT
            {pk},
            COUNT(*) AS count
        FROM stg_{table}
        GROUP BY {pk}
        HAVING COUNT(*) > 1
    """).df()

    print(
        f"{table:15} | "
        f"Duplicate PK = {len(result):,}"
    )

ถ้าผลลัพธ์เป็น Duplicate PK = 0 หมายความว่าไม่พบค่า Primary Key ซ้ำ ซึ่งเป็นแนวทางเดียวกับ Validation ในไฟล์ต้นฉบับ

ตรวจ Foreign Key
# ============================================
# FOREIGN KEY VALIDATION
# ============================================

# order_items -> orders
result = con.execute("""
SELECT COUNT(*) AS invalid_order
FROM stg_order_items oi
LEFT JOIN stg_orders o
    ON oi.order_id = o.order_id
WHERE o.order_id IS NULL
""").fetchone()[0]

print("Invalid order_id:", result)


# order_items -> products
result = con.execute("""
SELECT COUNT(*) AS invalid_product
FROM stg_order_items oi
LEFT JOIN stg_products p
    ON oi.product_id = p.product_id
WHERE p.product_id IS NULL
""").fetchone()[0]

print("Invalid product_id:", result)


# orders -> customers
result = con.execute("""
SELECT COUNT(*) AS invalid_customer
FROM stg_orders o
LEFT JOIN stg_customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
""").fetchone()[0]

print("Invalid customer_id:", result)


# products -> suppliers
result = con.execute("""
SELECT COUNT(*) AS invalid_supplier
FROM stg_products p
LEFT JOIN stg_suppliers s
    ON p.supplier_id = s.supplier_id
WHERE s.supplier_id IS NULL
""").fetchone()[0]

print("Invalid supplier_id:", result)

แนวทางนี้สอดคล้องกับการตรวจ Referential Integrity ของ customer_id ในโปรเจกต์ต้นฉบับ

โค้ด 1.5 ตรวจสอบ Final Data Warehouse
# ============================================
# 1.5 FINAL DATA WAREHOUSE VALIDATION
# ============================================

final_tables = [
    'dim_date',
    'dim_product',
    'dim_customer',
    'dim_store',
    'dim_promotion',
    'dim_supplier',
    'fact_sales',
    'fact_return',
    'fact_shipments',
    'fact_payments'
]

for table in final_tables:

    count = con.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(
        f"{table:20} : "
        f"{count:,} records"
    )
ตรวจโครงสร้างตาราง
# ============================================
# CHECK TABLE STRUCTURE
# ============================================

for table in final_tables:

    print("=" * 60)
    print(f"TABLE: {table}")

    result = con.execute(
        f"DESCRIBE {table}"
    ).df()

    display(result)
สรุปโครงสร้างสุดท้ายให้ตรงกับรูป
                     DIM_DATE
                        │
                        │ date_id
                        ▼
CUSTOMER ────────► FACT_SALES ◄──────── PRODUCT
                        │
                        │
STORE ───────────►     │     ◄──────── PROMOTION
                        │
                        │
                     SUPPLIER


                     DIM_DATE
                        │
                        ▼
                   FACT_RETURN
                   │    │    │
                   ▼    ▼    ▼
                PRODUCT CUSTOMER STORE


CUSTOMER ───────► FACT_SHIPMENTS ◄────── STORE
                         │
                         ▼
                      ORDER_ID


                     DIM_DATE
                        │
                        ▼
                   FACT_PAYMENTS
                    │    │    │
                    ▼    ▼    ▼
                 CUSTOMER STORE ORDER

```
## 1.6 สรุปกระบวนการ ELT

กระบวนการ ELT (Extract, Load, Transform) ของระบบ Retail Data Warehouse มีวัตถุประสงค์เพื่อรวบรวมและจัดเตรียมข้อมูลจากระบบต้นทางให้อยู่ในรูปแบบที่เหมาะสมสำหรับการจัดเก็บและวิเคราะห์ข้อมูลเชิงธุรกิจ โดยข้อมูลต้นทางประกอบด้วยไฟล์ CSV จำนวน 12 ตาราง ได้แก่ `employees`, `returns`, `products`, `suppliers`, `categories`, `promotions`, `stores`, `customers`, `payments`, `orders`, `order_items` และ `shipments`

ในขั้นตอน **Extract** ระบบใช้ภาษา Python ร่วมกับ Pandas ในการอ่านข้อมูลจากไฟล์ CSV และนำข้อมูลเข้าสู่ DataFrame เพื่อเตรียมเข้าสู่กระบวนการถัดไป จากนั้นในขั้นตอน **Load** ข้อมูลทั้งหมดจะถูกนำเข้าสู่ฐานข้อมูล DuckDB ในรูปแบบ Staging Tables โดยตั้งชื่อในรูปแบบ `stg_<table_name>` เพื่อใช้เป็นพื้นที่จัดเก็บข้อมูลระหว่าง Source Layer และ Data Warehouse ซึ่งช่วยให้สามารถตรวจสอบและจัดการคุณภาพของข้อมูลก่อนนำไปใช้ในขั้นตอน Transformation ได้

สำหรับขั้นตอน **Transform** ระบบจะทำการตรวจสอบและทำความสะอาดข้อมูล เช่น การตรวจสอบ Missing Values และ Duplicate Records รวมถึงตรวจสอบ Primary Key และ Foreign Key เพื่อให้มั่นใจว่าข้อมูลมีความถูกต้องและมีความสัมพันธ์ระหว่างตารางอย่างเหมาะสม นอกจากนี้ยังมีการแปลงชนิดข้อมูลให้ตรงกับลักษณะของข้อมูล เช่น การแปลงข้อมูลวันที่เป็นชนิด `DATE` การแปลงจำนวนสินค้าเป็น `INTEGER` และการแปลงข้อมูลราคา ส่วนลด ยอดคืนเงิน และจำนวนเงินเป็นชนิดตัวเลขสำหรับใช้ในการคำนวณ

หลังจากการทำความสะอาดข้อมูลแล้ว ระบบจะทำการจัดโครงสร้างข้อมูลให้อยู่ในรูปแบบ **Multidimensional Data Warehouse** ซึ่งประกอบด้วย Dimension Tables จำนวน 6 ตาราง ได้แก่ `Dim_Date`, `Dim_Product`, `Dim_Customer`, `Dim_Store`, `Dim_Promotion` และ `Dim_Supplier` โดย Dimension Tables ทำหน้าที่เก็บข้อมูลสำหรับใช้เป็นมิติในการวิเคราะห์ เช่น เวลา สินค้า ลูกค้า สาขา Promotion และ Supplier

ในส่วนของ Fact Tables ระบบประกอบด้วย 4 ตาราง ได้แก่ `Fact_Sales`, `Fact_Return`, `Fact_Shipments` และ `Fact_Payments` โดย `Fact_Sales` เป็น Fact Table หลักที่ใช้สำหรับวิเคราะห์ข้อมูลการขาย มี Grain เป็น 1 Order Line Item และประกอบด้วยข้อมูล `quantity`, `unit_price`, `sales_amount` และ `discount` โดย `sales_amount` คำนวณจากจำนวนสินค้าคูณด้วยราคาต่อหน่วย (`quantity × unit_price`) ส่วน `Fact_Return` ใช้จัดเก็บข้อมูลการคืนสินค้าและจำนวนเงินคืน `refund`, `Fact_Shipments` ใช้จัดเก็บข้อมูลการจัดส่งและสถานะการจัดส่ง และ `Fact_Payments` ใช้จัดเก็บข้อมูลธุรกรรมการชำระเงินและจำนวนเงิน `amount`

การสร้าง Fact Tables จำเป็นต้องมีการ JOIN ข้อมูลจากหลายตารางเพื่อให้ได้ข้อมูลที่สมบูรณ์ตาม Data Model ที่กำหนด เช่น `Fact_Sales` เชื่อมโยงข้อมูลระหว่าง `orders`, `order_items`, `products` และ `promotions` ขณะที่ `Fact_Return` เชื่อมโยงข้อมูล `returns` กับ `order_items` และ `orders` เพื่อให้สามารถระบุวันที่ สินค้า ลูกค้า และสาขาที่เกี่ยวข้องกับการคืนสินค้าได้ ส่วน `Fact_Shipments` และ `Fact_Payments` เชื่อมโยงกับ `orders` เพื่อดึงข้อมูลลูกค้าและสาขาที่เกี่ยวข้อง

ผลลัพธ์ของกระบวนการ ELT คือ Data Warehouse ที่มีโครงสร้างประกอบด้วย **12 Source Tables, 12 Staging Tables, 6 Dimension Tables และ 4 Fact Tables** โดยมีความสัมพันธ์ในลักษณะ **Multiple Star Schema หรือ Fact Constellation Schema** ซึ่ง Dimension Tables สามารถถูกใช้ร่วมกับ Fact Tables หลายชุด ทำให้สามารถวิเคราะห์ข้อมูลได้หลายมิติและเชื่อมโยงข้อมูลด้านการขาย การคืนสินค้า การจัดส่ง และการชำระเงินเข้าด้วยกัน

โดยรวมแล้ว กระบวนการ ELT สามารถสรุปได้เป็นลำดับ **Source CSV → Extract ด้วย Python/Pandas → Load เข้าสู่ DuckDB Staging → Data Cleaning และ Data Validation → Transform ด้วย SQL/DuckDB → Dimension และ Fact Tables → Multidimensional Data Warehouse** ซึ่งช่วยให้ข้อมูลมีความเป็นระบบ มีความถูกต้อง และพร้อมสำหรับการนำไปวิเคราะห์และสร้างรายงานเชิงธุรกิจต่อไป กระบวนการโดยรวมสอดคล้องกับแนวทาง ELT ของโปรเจกต์ที่ใช้ Source CSV, DuckDB Staging, Data Cleaning, Validation และ SQL Transformation ก่อนสร้าง Data Warehouse
# Dashborad Link
##อ้างอิง
Datarspectrum Technology Training Center. (n.d.). Retail Data Warehouse – 12 Table 1M+ Rows Dataset [Data set]. Kaggle.
https://www.kaggle.com/datasets/datarspectrum/retail-data-warehouse-12-table-1m-rows-dataset
