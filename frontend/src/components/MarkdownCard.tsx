import ReactMarkdown from "react-markdown";

type Props = {
  title: string;
  content?: string | null;
};

export function MarkdownCard({ title, content }: Props) {
  return (
    <div className="rounded-3xl border border-black/5 bg-white p-5 shadow-card">
      <div className="mb-4 text-lg font-semibold">{title}</div>
      <div className="prose prose-slate max-w-none text-sm">
        <ReactMarkdown>{content || "_暂无内容_"}</ReactMarkdown>
      </div>
    </div>
  );
}

