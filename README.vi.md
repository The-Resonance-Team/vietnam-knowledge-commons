# Kho tri thức chung Việt Nam (VNKC)

> Tri thức về Việt Nam — đã kiểm chứng, có phiên bản, sẵn sàng cho máy tính.

VNKC xây dựng nền tảng tri thức mở, có thể kiểm chứng, có phiên bản và máy đọc được về Việt Nam — văn bản quy phạm pháp luật, thủ tục hành chính và biểu mẫu chính thức, thuế, đất đai, lao động, bảo hiểm xã hội, thống kê, địa lý hành chính và nhiều lĩnh vực khác. Đây là **hạ tầng tri thức quốc gia**, không phải một dự án thu thập web đơn thuần.

**Trạng thái: Giai đoạn 0** — nghiên cứu, mô hình dữ liệu, đăng ký nguồn và công cụ kiểm định. Chưa thu thập dữ liệu hàng loạt.

[English README](./README.md)

## Kiến trúc: ba lớp, tách biệt rõ ràng

| Lớp                | Nội dung                                                                                                                               | Thay đổi?                                  |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| **Nguồn**          | Bản chụp/tham chiếu bất biến tới tài liệu chính thống, kèm nguồn gốc, checksum và tình trạng giấy phép                                 | Chỉ thêm, không ghi đè                     |
| **Tri thức chuẩn** | Bản ghi chuẩn hóa, khử trùng lặp, có nhận thức thời gian (văn bản, thủ tục, biểu mẫu, tổ chức, đơn vị hành chính, quan hệ)             | Có phiên bản                               |
| **Bộ dữ liệu ML**  | Các gói dẫn xuất có phiên bản rõ ràng (pretraining, truy hồi, instruction tuning, hỏi-đáp, suy luận pháp lý theo thời gian, benchmark) | Phát hành kèm checksum và bản kê giấy phép |

Câu hỏi về pháp luật hiện hành được trả lời bằng **truy hồi có phiên bản kèm trích dẫn** — không bằng trọng số mô hình.

## Bắt đầu nhanh

```bash
pnpm install
pnpm run check          # prettier + typecheck + ranh giới module + tests + kiểm định registry/ví dụ

pnpm vnkc validate-sources              # kiểm định registry/sources.yaml
pnpm vnkc validate-record --all examples
pnpm vnkc report-sources                # báo cáo tầng / giấy phép / độ tin cậy

cd packages/sdk-python && uv sync && uv run pytest && uv run ruff check .
```

## Nguyên tắc nền tảng

1. **Nguồn chính thống trước tiên.** Phân tầng A–D; tầng D không bao giờ là căn cứ chuẩn.
2. **Mọi bản ghi đều có nguồn gốc** — URL nguồn, ngày thu thập, phương thức, checksum, tình trạng giấy phép, độ tin cậy.
3. **Không bao giờ bịa đặt** giấy phép, API, endpoint, URL, số hiệu văn bản hay tình trạng pháp lý. Không rõ → `unknown`; giấy phép mặc định `reference-only`.
4. **Bảo tồn lịch sử.** Ngày ban hành, ngày thu thập và hiệu lực pháp lý là ba khái niệm khác nhau; truy vấn "có hiệu lực tại ngày X" là tính năng hạng nhất.
5. **Không dữ liệu cá nhân.** Không biểu mẫu đã điền, không thông tin xác thực, không nội dung nhạy cảm.
6. **Tài liệu nguồn ≠ nội dung dẫn xuất.** Tóm tắt/hỏi-đáp do máy tạo là dữ liệu dẫn xuất, không phải căn cứ pháp lý.

Xem [DATA_POLICY.md](./DATA_POLICY.md), [DATA_LICENSES.md](./DATA_LICENSES.md) và các tài liệu nghiên cứu trong `docs/research/`.

## Giấy phép

- **Mã nguồn** (schemas, SDK, CLI, tài liệu): [Apache-2.0](./LICENSE)
- **Dữ liệu nguồn thu thập**: bản kê giấy phép theo từng nguồn — xem [DATA_LICENSES.md](./DATA_LICENSES.md). Cố ý **không có** một giấy phép chung cho toàn bộ dữ liệu.

## Tuyên bố miễn trừ

VNKC không phải tư vấn pháp lý. Nội dung dẫn xuất (tóm tắt, hỏi-đáp, hướng dẫn) không thay thế văn bản chính thức hay tư vấn viên có chuyên môn.
