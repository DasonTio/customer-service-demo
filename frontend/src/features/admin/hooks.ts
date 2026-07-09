import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { deleteDocument, fetchDocuments, uploadDocument } from '../../api/client'

const DOCUMENTS_KEY = ['documents']

export function useDocuments() {
  return useQuery({ queryKey: DOCUMENTS_KEY, queryFn: fetchDocuments })
}

export function useUploadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY }),
  })
}

export function useDeleteDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY }),
  })
}
