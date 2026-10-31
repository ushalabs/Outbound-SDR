import * as Dialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { Button } from './ui/button'

export function Modal({
  title,
  children,
  close,
}: {
  title: string
  children: React.ReactNode
  close: () => void
}) {
  return (
    <Dialog.Root
      open
      onOpenChange={(open) => {
        if (!open) close()
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay className="modal-backdrop" />
        <Dialog.Content className="modal modal-dialog-content">
          <div className="modal-heading">
            <Dialog.Title asChild>
              <h2>{title}</h2>
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" aria-label="Close dialog">
                <X size={19} />
              </Button>
            </Dialog.Close>
          </div>
          <Dialog.Description className="sr-only">
            {title}. Complete the fields or choose an action, or close this dialog to return.
          </Dialog.Description>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
export function Badge({ value }: { value: string }) {
  return <span className={`badge badge-${value}`}>{value.replaceAll('_', ' ')}</span>
}
