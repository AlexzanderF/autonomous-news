import ReactMarkdown from 'react-markdown';

interface ArticleContentProps {
  content: string;
}

export default function ArticleContent({ content }: ArticleContentProps) {
  return (
    <article className="max-w-none">
      <div className="article-content text-lg text-slate-900 leading-relaxed">
        <ReactMarkdown
          components={{
            h2: ({ node: _node, ...props }) => <h2 className="text-slate-900 mt-6 mb-6" {...props} />,
            h3: ({ node: _node, ...props }) => <h3 className="text-slate-900 mt-6 mb-6" {...props} />,
            h4: ({ node: _node, ...props }) => <h4 className="text-slate-900 mt-6 mb-6" {...props} />,
            p: ({ node: _node, ...props }) => <p className="mt-4" {...props} />,
            ul: ({ node: _node, ...props }) => <ul className="my-4 list-disc list-outside pl-5 space-y-2" {...props} />,
            ol: ({ node: _node, ...props }) => <ol className="my-4 list-decimal list-outside pl-5 space-y-2" {...props} />,
            hr: ({ node: _node, ...props }) => <hr className="my-8 border-slate-300" {...props} />,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </article>
  );
}
